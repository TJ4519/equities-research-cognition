from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator

from .errors import IntegrityError, ValidationError
from .records import validate_payload
from .util import (
    atomic_write,
    canonical_json,
    digest_bytes,
    digest_json,
    ensure_inside,
    new_id,
    read_regular_file,
    utc_now,
    verify_digest,
)


@dataclass(frozen=True)
class StoredObject:
    id: str
    kind: str
    payload: dict[str, Any]
    digest: str
    created_at: str


@dataclass(frozen=True)
class StoredRelation:
    id: int
    subject_id: str
    predicate: str
    object_id: str
    payload: dict[str, Any]
    digest: str
    created_at: str


@dataclass(frozen=True)
class StoredBlob:
    digest: str
    size: int
    media_type: str
    relative_path: str
    created_at: str


class WorkspaceStore:
    """Append-only local object graph and content-addressed byte store."""

    CONTROL_DIR = ".research"
    DATABASE = "workspace.db"

    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        self.control = self.root / self.CONTROL_DIR
        self.database = self.control / self.DATABASE
        self.objects_root = self.control / "objects"
        self.contexts_root = self.control / "contexts"
        self.runs_root = self.control / "runs"
        self.replays_root = self.control / "replays"
        if not self.database.is_file():
            raise ValidationError(f"workspace is not initialised: {self.root}")

    @classmethod
    def initialise(cls, root: Path, *, title: str = "Local research workspace") -> "WorkspaceStore":
        root = root.expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        control = root / cls.CONTROL_DIR
        if control.exists() and control.is_symlink():
            raise ValidationError("workspace control directory cannot be a symlink")
        control.mkdir(mode=0o700, exist_ok=True)
        for name in ("objects", "contexts", "runs", "replays", "exports"):
            directory = control / name
            directory.mkdir(mode=0o700, exist_ok=True)
            if directory.is_symlink():
                raise ValidationError(f"workspace directory cannot be a symlink: {directory}")
        database = control / cls.DATABASE
        connection = sqlite3.connect(database)
        try:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                PRAGMA synchronous=FULL;
                PRAGMA foreign_keys=ON;

                CREATE TABLE IF NOT EXISTS workspace_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS objects (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    digest TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id TEXT NOT NULL REFERENCES objects(id),
                    predicate TEXT NOT NULL,
                    object_id TEXT NOT NULL REFERENCES objects(id),
                    payload_json TEXT NOT NULL,
                    digest TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(subject_id, predicate, object_id, digest)
                );

                CREATE TABLE IF NOT EXISTS blobs (
                    digest TEXT PRIMARY KEY,
                    size INTEGER NOT NULL,
                    media_type TEXT NOT NULL,
                    relative_path TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS objects_kind_idx ON objects(kind, created_at);
                CREATE INDEX IF NOT EXISTS relations_subject_idx ON relations(subject_id, predicate);
                CREATE INDEX IF NOT EXISTS relations_object_idx ON relations(object_id, predicate);

                CREATE TRIGGER IF NOT EXISTS objects_no_update
                BEFORE UPDATE ON objects BEGIN
                    SELECT RAISE(ABORT, 'objects are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS objects_no_delete
                BEFORE DELETE ON objects BEGIN
                    SELECT RAISE(ABORT, 'objects are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS relations_no_update
                BEFORE UPDATE ON relations BEGIN
                    SELECT RAISE(ABORT, 'relations are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS relations_no_delete
                BEFORE DELETE ON relations BEGIN
                    SELECT RAISE(ABORT, 'relations are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS blobs_no_update
                BEFORE UPDATE ON blobs BEGIN
                    SELECT RAISE(ABORT, 'blobs are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS blobs_no_delete
                BEFORE DELETE ON blobs BEGIN
                    SELECT RAISE(ABORT, 'blobs are append-only');
                END;
                """
            )
            created_at = utc_now()
            connection.execute(
                "INSERT OR IGNORE INTO workspace_meta(key, value) VALUES (?, ?)",
                ("schema_version", "local-research-workspace/v1"),
            )
            connection.execute(
                "INSERT OR IGNORE INTO workspace_meta(key, value) VALUES (?, ?)",
                ("created_at", created_at),
            )
            connection.execute(
                "INSERT OR IGNORE INTO workspace_meta(key, value) VALUES (?, ?)",
                ("title", title.strip() or "Local research workspace"),
            )
            connection.commit()
        finally:
            connection.close()
        return cls(root)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    @contextmanager
    def read_connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def meta(self) -> dict[str, str]:
        with self.read_connection() as connection:
            rows = connection.execute("SELECT key, value FROM workspace_meta ORDER BY key")
            return {str(row["key"]): str(row["value"]) for row in rows}

    def put_object(
        self,
        kind: str,
        payload: dict[str, Any],
        *,
        object_id: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> StoredObject:
        payload = validate_payload(kind, payload)
        object_id = object_id or new_id(kind)
        created_at = utc_now()
        envelope = {
            "id": object_id,
            "kind": kind,
            "payload": payload,
            "created_at": created_at,
        }
        digest = digest_json(envelope)
        payload_json = canonical_json(payload)

        def insert(target: sqlite3.Connection) -> None:
            target.execute(
                "INSERT INTO objects(id, kind, payload_json, digest, created_at) VALUES (?, ?, ?, ?, ?)",
                (object_id, kind, payload_json, digest, created_at),
            )

        if connection is not None:
            insert(connection)
        else:
            with self.transaction() as target:
                insert(target)
        return StoredObject(object_id, kind, payload, digest, created_at)

    def get_object(self, object_id: str) -> StoredObject:
        with self.read_connection() as connection:
            row = connection.execute(
                "SELECT id, kind, payload_json, digest, created_at FROM objects WHERE id = ?",
                (object_id,),
            ).fetchone()
        if row is None:
            raise ValidationError(f"unknown workspace object: {object_id}")
        payload = json.loads(row["payload_json"])
        return StoredObject(
            id=str(row["id"]),
            kind=str(row["kind"]),
            payload=payload,
            digest=str(row["digest"]),
            created_at=str(row["created_at"]),
        )

    def list_objects(self, kind: str | None = None) -> list[StoredObject]:
        query = "SELECT id, kind, payload_json, digest, created_at FROM objects"
        values: tuple[Any, ...] = ()
        if kind is not None:
            query += " WHERE kind = ?"
            values = (kind,)
        query += " ORDER BY created_at, id"
        with self.read_connection() as connection:
            rows = connection.execute(query, values).fetchall()
        return [
            StoredObject(
                id=str(row["id"]),
                kind=str(row["kind"]),
                payload=json.loads(row["payload_json"]),
                digest=str(row["digest"]),
                created_at=str(row["created_at"]),
            )
            for row in rows
        ]

    def put_relation(
        self,
        subject_id: str,
        predicate: str,
        object_id: str,
        payload: dict[str, Any] | None = None,
        *,
        connection: sqlite3.Connection | None = None,
    ) -> StoredRelation:
        predicate = predicate.strip()
        if not predicate:
            raise ValidationError("relation predicate is required")
        self.get_object(subject_id)
        self.get_object(object_id)
        payload = payload or {}
        if not isinstance(payload, dict):
            raise ValidationError("relation payload must be a JSON object")
        created_at = utc_now()
        envelope = {
            "subject_id": subject_id,
            "predicate": predicate,
            "object_id": object_id,
            "payload": payload,
            "created_at": created_at,
        }
        digest = digest_json(envelope)
        payload_json = canonical_json(payload)

        def insert(target: sqlite3.Connection) -> int:
            cursor = target.execute(
                "INSERT INTO relations(subject_id, predicate, object_id, payload_json, digest, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (subject_id, predicate, object_id, payload_json, digest, created_at),
            )
            return int(cursor.lastrowid)

        if connection is not None:
            relation_id = insert(connection)
        else:
            with self.transaction() as target:
                relation_id = insert(target)
        return StoredRelation(
            relation_id,
            subject_id,
            predicate,
            object_id,
            payload,
            digest,
            created_at,
        )

    def relations_from(self, subject_id: str, predicate: str | None = None) -> list[StoredRelation]:
        query = (
            "SELECT id, subject_id, predicate, object_id, payload_json, digest, created_at "
            "FROM relations WHERE subject_id = ?"
        )
        values: list[Any] = [subject_id]
        if predicate is not None:
            query += " AND predicate = ?"
            values.append(predicate)
        query += " ORDER BY created_at, id"
        with self.read_connection() as connection:
            rows = connection.execute(query, tuple(values)).fetchall()
        return [self._relation_from_row(row) for row in rows]

    def relations_to(self, object_id: str, predicate: str | None = None) -> list[StoredRelation]:
        query = (
            "SELECT id, subject_id, predicate, object_id, payload_json, digest, created_at "
            "FROM relations WHERE object_id = ?"
        )
        values: list[Any] = [object_id]
        if predicate is not None:
            query += " AND predicate = ?"
            values.append(predicate)
        query += " ORDER BY created_at, id"
        with self.read_connection() as connection:
            rows = connection.execute(query, tuple(values)).fetchall()
        return [self._relation_from_row(row) for row in rows]

    @staticmethod
    def _relation_from_row(row: sqlite3.Row) -> StoredRelation:
        return StoredRelation(
            id=int(row["id"]),
            subject_id=str(row["subject_id"]),
            predicate=str(row["predicate"]),
            object_id=str(row["object_id"]),
            payload=json.loads(row["payload_json"]),
            digest=str(row["digest"]),
            created_at=str(row["created_at"]),
        )

    def put_blob(self, content: bytes, *, media_type: str = "application/octet-stream") -> StoredBlob:
        if not isinstance(content, bytes):
            raise ValidationError("blob content must be bytes")
        media_type = media_type.strip() or "application/octet-stream"
        digest = digest_bytes(content)
        relative = Path(digest[:2]) / digest[2:4] / digest
        target = ensure_inside(self.objects_root, self.objects_root / relative)
        created_at = utc_now()
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT digest, size, media_type, relative_path, created_at FROM blobs WHERE digest = ?",
                (digest,),
            ).fetchone()
            if existing is not None:
                blob = StoredBlob(
                    digest=str(existing["digest"]),
                    size=int(existing["size"]),
                    media_type=str(existing["media_type"]),
                    relative_path=str(existing["relative_path"]),
                    created_at=str(existing["created_at"]),
                )
                verify_digest(self.read_blob(blob.digest), digest, "existing blob")
                return blob
            atomic_write(target, content)
            connection.execute(
                "INSERT INTO blobs(digest, size, media_type, relative_path, created_at) VALUES (?, ?, ?, ?, ?)",
                (digest, len(content), media_type, relative.as_posix(), created_at),
            )
        return StoredBlob(digest, len(content), media_type, relative.as_posix(), created_at)

    def get_blob(self, digest: str) -> StoredBlob:
        with self.read_connection() as connection:
            row = connection.execute(
                "SELECT digest, size, media_type, relative_path, created_at FROM blobs WHERE digest = ?",
                (digest,),
            ).fetchone()
        if row is None:
            raise ValidationError(f"unknown blob: {digest}")
        return StoredBlob(
            digest=str(row["digest"]),
            size=int(row["size"]),
            media_type=str(row["media_type"]),
            relative_path=str(row["relative_path"]),
            created_at=str(row["created_at"]),
        )

    def blob_path(self, digest: str) -> Path:
        blob = self.get_blob(digest)
        return ensure_inside(self.objects_root, self.objects_root / blob.relative_path)

    def read_blob(self, digest: str) -> bytes:
        blob = self.get_blob(digest)
        path = ensure_inside(self.objects_root, self.objects_root / blob.relative_path)
        content = read_regular_file(path, max_bytes=blob.size)
        if len(content) != blob.size:
            raise IntegrityError(f"blob size mismatch: {digest}")
        verify_digest(content, digest, "blob")
        return content

    def verify_object(self, object_id: str) -> bool:
        item = self.get_object(object_id)
        validate_payload(item.kind, item.payload)
        envelope = {
            "id": item.id,
            "kind": item.kind,
            "payload": item.payload,
            "created_at": item.created_at,
        }
        observed = digest_json(envelope)
        if observed != item.digest:
            raise IntegrityError(f"object digest mismatch: {object_id}")
        return True

    def verify_relation(self, relation: StoredRelation) -> bool:
        envelope = {
            "subject_id": relation.subject_id,
            "predicate": relation.predicate,
            "object_id": relation.object_id,
            "payload": relation.payload,
            "created_at": relation.created_at,
        }
        if digest_json(envelope) != relation.digest:
            raise IntegrityError(f"relation digest mismatch: {relation.id}")
        self.get_object(relation.subject_id)
        self.get_object(relation.object_id)
        return True

    def verify_all(self) -> dict[str, int]:
        objects = self.list_objects()
        for item in objects:
            self.verify_object(item.id)
        relations: list[StoredRelation] = []
        with self.read_connection() as connection:
            rows = connection.execute(
                "SELECT id, subject_id, predicate, object_id, payload_json, digest, created_at "
                "FROM relations ORDER BY id"
            ).fetchall()
            relations = [self._relation_from_row(row) for row in rows]
        for relation in relations:
            self.verify_relation(relation)
        with self.read_connection() as connection:
            blob_rows = connection.execute("SELECT digest FROM blobs ORDER BY digest").fetchall()
        for row in blob_rows:
            self.read_blob(str(row["digest"]))
        return {
            "objects": len(objects),
            "relations": len(relations),
            "blobs": len(blob_rows),
        }
