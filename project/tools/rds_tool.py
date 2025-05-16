#rdstool
import traceback                      # 예외 트레이스백 출력
import mysql.connector                # MySQL DB 연결
from typing import Type              # args_schema 타입 힌트용
from pydantic import BaseModel        # Tool 입력 타입 정의용
from langchain.tools import BaseTool  # LangChain 사용자 정의 Tool 기반 클래스
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class MySQLQueryInput(BaseModel):
    query: str

class MySQLQueryTool(BaseTool):
    name: str = "mysql_query_tool"
    description: str = "\nRDS의 MySQL에 SELECT 쿼리를 날릴 수 있는 도구입니다. 반드시 SELECT 문만 사용하세요.\n"
    args_schema: Type[BaseModel] = MySQLQueryInput

    host: str
    user: str
    password: str
    database: str

    def _run(self, query: str):
        if not query.strip().lower().startswith("select"):
            return "오직 SELECT 쿼리만 허용됩니다."

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            result = [dict(zip(column_names, row)) for row in rows]
            return result or "결과 없음"
        except Exception as e:
            return f"오류 발생: {e}\n{traceback.format_exc()}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _arun(self, query: str):
        raise NotImplementedError("비동기 버전은 지원하지 않습니다.")
    

rds_tool = MySQLQueryTool(
    name="rds_query_tool",
    host="localhost",
    user="root",
    password="root",
    database="senpick_db"
)
__all__ = ["rds_tool"]