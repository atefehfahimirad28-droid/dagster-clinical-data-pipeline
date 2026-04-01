"""PostgreSQL resource for the Charite clinical analytics pipeline.

Provides database connectivity for all pipeline assets.

German: PostgreSQL-Ressource fuer die klinische Analyse-Pipeline der Charite.

Stellt Datenbankverbindungen fuer alle Pipeline-Assets bereit.
"""

import dagster as dg
import psycopg2
from psycopg2 import sql


class PostgresResource(dg.ConfigurableResource):
    """A configurable resource that manages PostgreSQL connections.

    Attributes:
        connection_string: PostgreSQL connection string in the format
            postgresql://user:password@host:port/database

    DE: Eine konfigurierbare Ressource, die PostgreSQL-Verbindungen verwaltet.
    """

    connection_string: str = (
        "postgresql://clinicflow:clinicflow@localhost:5432/clinicflow"
    )

    def get_connection(self):
        """Return a new psycopg2 connection to the configured database.

        Returns:
            psycopg2 connection object

        Hints:
            - Use psycopg2.connect() with the connection_string
            - The connection string is already stored in self.connection_string

        DE: Gibt eine neue psycopg2-Verbindung zur konfigurierten Datenbank zurueck.
        """
        return psycopg2.connect(self.connection_string)

    def execute_query(self, query: str, params: tuple | None = None) -> list:
        """Execute a SQL query and return results.

        Args:
            query: SQL query string (may contain %s placeholders)
            params: Optional tuple of parameters for the query

        Returns:
            List of rows (tuples) for SELECT queries, empty list for others

        Hints:
            - Get a connection using self.get_connection()
            - Use a cursor to execute the query
            - For SELECT queries, fetchall() the results
            - Always commit and close the connection
            - Use try/finally to ensure cleanup

        DE: Fuehrt eine SQL-Abfrage aus und gibt die Ergebnisse zurueck.
        """
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            if cur.description:  # SELECT query
                results = cur.fetchall()
            else:
                results = []
            conn.commit()
            return results
        finally:
            conn.close()

    def load_rows(self, rows: list[dict], table_name: str) -> int:
        """Bulk-insert a list of dicts into the specified table.

        Args:
            rows: list of dicts whose keys match the target table columns
            table_name: Name of the PostgreSQL table to insert into

        Returns:
            Number of rows inserted

        Hints:
            - Get a connection using self.get_connection()
            - Use rows[0].keys() to get column names
            - Build an INSERT statement with %s placeholders for each column
            - Use cursor.executemany() for efficient bulk insert
            - Consider TRUNCATING the table first (idempotent loads)
            - Commit and close the connection

        DE: Fuegt eine Liste von Dicts per Masseneinfuegung in die
        angegebene Tabelle ein.
        """
        if not rows:
            return 0

        conn = self.get_connection()
        try:
            with conn, conn.cursor() as cur:
                # Use psycopg2.sql to safely handle identifiers
                cur.execute(
                    sql.SQL("TRUNCATE TABLE {} CASCADE").format(
                        sql.Identifier(table_name)
                    )
                )
                cols = list(rows[0].keys())
                insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                    sql.Identifier(table_name),
                    sql.SQL(", ").join(map(sql.Identifier, cols)),
                    sql.SQL(", ").join([sql.Placeholder()] * len(cols)),
                )
                values = [tuple(row[c] for c in cols) for row in rows]
                cur.executemany(insert_sql, values)
                return len(values)
        finally:
            conn.close()
