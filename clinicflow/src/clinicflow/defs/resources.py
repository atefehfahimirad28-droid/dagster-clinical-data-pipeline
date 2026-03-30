"""PostgreSQL resource for the Charite clinical analytics pipeline.

Students implement the TODO stubs to provide database connectivity
for all pipeline assets.

German: PostgreSQL-Ressource fuer die klinische Analyse-Pipeline der Charite.

Studierende implementieren die TODO-Stubs, um Datenbankverbindungen
fuer alle Pipeline-Assets bereitzustellen.
"""

import dagster as dg


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
        # TODO: Implement this method (Task 1)
        # TODO (DE): Implementiere diese Methode (Aufgabe 1)
        # Hint: return psycopg2.connect(self.connection_string)
        raise NotImplementedError("TODO: Implement get_connection()")

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
        # TODO: Implement this method (Task 1)
        # TODO (DE): Implementiere diese Methode (Aufgabe 1)
        # Hint:
        #   conn = self.get_connection()
        #   try:
        #       cur = conn.cursor()
        #       cur.execute(query, params)
        #       if cur.description:  # SELECT query
        #           results = cur.fetchall()
        #       else:
        #           results = []
        #       conn.commit()
        #       return results
        #   finally:
        #       conn.close()
        raise NotImplementedError("TODO: Implement execute_query()")

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
        # TODO: Implement this method (Task 1)
        # TODO (DE): Implementiere diese Methode (Aufgabe 1)
        # Hint:
        #   conn = self.get_connection()
        #   try:
        #       cur = conn.cursor()
        #       cur.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        #       cols = list(rows[0].keys())
        #       col_str = ", ".join(cols)
        #       placeholders = ", ".join(["%s"] * len(cols))
        #       insert_sql = (
        #           f"INSERT INTO {table_name} ({col_str}) "
        #           f"VALUES ({placeholders})"
        #       )
        #       values = [tuple(row[c] for c in cols) for row in rows]
        #       cur.executemany(insert_sql, values)
        #       conn.commit()
        #       return len(values)
        #   finally:
        #       conn.close()
        raise NotImplementedError("TODO: Implement load_rows()")
