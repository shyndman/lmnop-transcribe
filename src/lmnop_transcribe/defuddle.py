import asyncio
import shlex
import tempfile

from pydantic import BaseModel


class DefuddleResult(BaseModel):
  markdown: str


async def defuddle(input_html: str, url: str | None = None):
  with tempfile.NamedTemporaryFile(mode="w", suffix=".html") as tmp:
    tmp.write(input_html)
    tmp.flush()
    md_proc = await asyncio.create_subprocess_shell(
      f"defuddle parse --markdown {shlex.quote(tmp.name)}",
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE,
      shell=True,
    )

    (md_bytes, _) = await md_proc.communicate()

    print(f"done {url}")
    return DefuddleResult(markdown=str(md_bytes, "utf-8"))
