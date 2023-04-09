def create_user_partition(target, connection, **kw) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_2023"
        PARTITION OF public.user
        FOR VALUES FROM ('2023-01-01') TO ('2023-12-31');"""
    )
