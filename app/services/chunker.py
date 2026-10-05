import re
from pathlib import Path
from typing import List, Dict, Any, Optional

def clean_text(text: str) -> str:
    """Normalizes whitespace and removes unwanted control characters."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Replace 3 or more newlines with two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def split_sentences(text: str) -> List[str]:
    """Splits text into sentences keeping punctuation attached."""
    pattern = r"(?<=[.!?])\s+"
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if p.strip()]

def chunk_text(text: str, max_chars: int = 1000) -> List[Dict[str, Any]]:
    """
    Intelligently chunks long text into natural paragraph/sentence-sized segments.
    Each chunk respects sentence boundaries and targets approximately max_chars.
    Returns list of dicts: [{'index': 0, 'text': '...', 'char_count': 123, 'word_count': 25}]
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    # First split by paragraphs
    paragraphs = cleaned.split("\n\n")
    chunks: List[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph stays within limit
        if len(current_chunk) + len(para) + 2 <= max_chars:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
        else:
            # If current chunk has content, commit it
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            # If the paragraph itself exceeds max_chars, split by sentences
            if len(para) > max_chars:
                sentences = split_sentences(para)
                temp_chunk = ""
                for sent in sentences:
                    if len(temp_chunk) + len(sent) + 1 <= max_chars:
                        temp_chunk = f"{temp_chunk} {sent}".strip()
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                            temp_chunk = ""
                        # If a single sentence exceeds max_chars, split on punctuation or words
                        if len(sent) > max_chars:
                            words = sent.split(" ")
                            w_chunk = ""
                            for w in words:
                                if len(w_chunk) + len(w) + 1 <= max_chars:
                                    w_chunk = f"{w_chunk} {w}".strip()
                                else:
                                    if w_chunk:
                                        chunks.append(w_chunk)
                                    w_chunk = w
                            if w_chunk:
                                temp_chunk = w_chunk
                        else:
                            temp_chunk = sent
                if temp_chunk:
                    current_chunk = temp_chunk
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    result = []
    for idx, c in enumerate(chunks):
        c = c.strip()
        if c:
            result.append({
                "index": idx,
                "text": c,
                "char_count": len(c),
                "word_count": len(c.split())
            })
    return result

def detect_chapters(text: str) -> List[Dict[str, Any]]:
    """
    Detects potential chapters or sections in long book text.
    """
    lines = clean_text(text).split("\n")
    chapter_pattern = re.compile(
        r"^(chapter\s+\d+|chapter\s+[ivxlcdm]+|prologue|epilogue|part\s+\d+|book\s+\d+|section\s+\d+|act\s+\d+|#\s+.+)",
        re.IGNORECASE
    )

    chapters = []
    current_title = "Introduction"
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if chapter_pattern.match(stripped) and len(stripped) < 80:
            if current_lines:
                ch_text = "\n".join(current_lines).strip()
                if ch_text:
                    chapters.append({
                        "title": current_title,
                        "text": ch_text,
                        "word_count": len(ch_text.split())
                    })
                current_lines = []
            current_title = stripped.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        ch_text = "\n".join(current_lines).strip()
        if ch_text:
            chapters.append({
                "title": current_title,
                "text": ch_text,
                "word_count": len(ch_text.split())
            })

    # If no distinct chapters found, treat whole text as single chapter
    if not chapters:
        chapters = [{
            "title": "Full Document",
            "text": text,
            "word_count": len(text.split())
        }]

    return chapters

def extract_text_from_file(file_path: Path, filename: str) -> str:
    """
    Extracts text from txt, md, pdf, epub, or html files.
    """
    ext = Path(filename).suffix.lower()

    if ext in [".txt", ".md", ".text"]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            pages_text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
            return "\n\n".join(pages_text)
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")

    elif ext in [".html", ".htm", ".xhtml"]:
        try:
            from bs4 import BeautifulSoup
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                return soup.get_text(separator="\n\n")
        except Exception as e:
            raise RuntimeError(f"Failed to extract HTML text: {str(e)}")

    elif ext == ".epub":
        try:
            import zipfile
            from bs4 import BeautifulSoup
            text_parts = []
            with zipfile.ZipFile(file_path, "r") as z:
                for name in z.namelist():
                    if name.endswith((".html", ".xhtml", ".xml")) and "toc" not in name.lower():
                        content = z.read(name).decode("utf-8", errors="ignore")
                        soup = BeautifulSoup(content, "html.parser")
                        text_parts.append(soup.get_text(separator="\n\n"))
            return "\n\n".join(text_parts)
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from EPUB: {str(e)}")

    raise ValueError(f"Unsupported file format: {ext}. Please upload .txt, .md, .pdf, or .epub")
