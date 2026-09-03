import logging
import psycopg2
import streamlit as st


class PostgreSQLHandler(logging.Handler):

    def emit(self, record):
        try:
            conn = psycopg2.connect(
                st.secrets["postgres"]["url"]
            )

            cursor = conn.cursor()
            vol_emailid = getattr(record, "vol_email_id", None)
            vol_phone_num = getattr(record, "vol_phone_num", None)
            ip_address = getattr(record, "ip_address", None)


            cursor.execute(
                """
                INSERT INTO vsp_app_logs
                (
                    log_level,
                    logger_name,
                    message,
                    module,
                    function_name,
                    line_number,
                    vol_email_id,
                    vol_phone_num,
                    ip_address
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    record.levelname,
                    record.name,
                    record.getMessage(),
                    record.module,
                    record.funcName,
                    record.lineno,
                    vol_emailid,
                    vol_phone_num,
                    ip_address
                )
            )

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            # Don't allow logging failures to crash the Streamlit app
            pass