"""
찬미예수 2000 악보 웹사이트 준비 스크립트
=========================================
실행 방법: 명령 프롬프트에서 이 파일이 있는 폴더로 이동 후
  python prepare.py

필요 패키지를 자동으로 설치합니다.
"""

import subprocess, sys, json
from pathlib import Path

# ── 경로 설정 (필요시 수정) ─────────────────────────────────────────────────
BASE_DIR = Path(r"C:\Users\sungm\Downloads\찬미 예수 2000 전곡 악보(교회,성경)\찬미 예수 2000 전곡 악보")
XLS_FILE = BASE_DIR / "복음성가2000목차_1.xls"
# BMP 폴더가 여러 개일 수 있으므로 모두 검색
BMP_FOLDERS = list(BASE_DIR.glob("찬미예수2000 악보 *"))

OUTPUT_DIR = Path(__file__).parent   # prepare.py 가 있는 폴더
IMAGES_DIR = OUTPUT_DIR / "images"
SONGS_JSON  = OUTPUT_DIR / "songs.json"
# ─────────────────────────────────────────────────────────────────────────────


def install_packages():
    pkgs = ["xlrd", "Pillow"]
    print("필요 패키지 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet"] + pkgs, check=True)
    print("패키지 설치 완료\n")


def read_xls():
    """XLS 파일에서 곡 번호, 제목, 가사 추출"""
    import xlrd
    songs = {}

    if not XLS_FILE.exists():
        print(f"⚠ XLS 파일을 찾을 수 없습니다: {XLS_FILE}")
        return songs

    print(f"XLS 읽는 중: {XLS_FILE.name}")
    wb = xlrd.open_workbook(str(XLS_FILE), encoding_override="cp949")

    for sheet_idx in range(wb.nsheets):
        ws = wb.sheet_by_index(sheet_idx)
        print(f"  시트 [{sheet_idx}] '{ws.name}': {ws.nrows}행 × {ws.ncols}열")

        # 첫 5행 미리보기
        for r in range(min(5, ws.nrows)):
            print(f"    행{r}: {ws.row_values(r)}")

        # 데이터 파싱 시도
        for r in range(ws.nrows):
            row = ws.row_values(r)
            if not row:
                continue

            # 첫 번째 셀이 숫자(곡 번호)인 경우
            num_cell = row[0]
            if isinstance(num_cell, (int, float)) and num_cell > 0:
                num = int(num_cell)
                title = str(row[1]).strip() if len(row) > 1 else ""
                lyrics = str(row[2]).strip() if len(row) > 2 else ""
                # 빈 문자열 정리
                if title in ("", "None"):
                    title = f"곡 {num}"
                songs[num] = {
                    "number": num,
                    "title": title,
                    "lyrics": lyrics,
                }

    print(f"  → {len(songs)}곡 추출\n")
    return songs


def convert_bmp_to_png(songs):
    """BMP → PNG 변환 (파일 크기 대폭 감소)"""
    from PIL import Image

    IMAGES_DIR.mkdir(exist_ok=True)
    converted = 0
    skipped = 0

    if not BMP_FOLDERS:
        print("⚠ BMP 폴더를 찾을 수 없습니다.")
        return songs

    for folder in sorted(BMP_FOLDERS):
        print(f"이미지 변환 중: {folder.name}")
        for bmp in sorted(folder.glob("*.bmp")):
            num_str = bmp.stem.strip("()")
            try:
                num = int(num_str)
            except ValueError:
                continue

            png_path = IMAGES_DIR / f"{num}.png"
            if png_path.exists():
                skipped += 1
            else:
                try:
                    img = Image.open(bmp)
                    # 흑백 변환으로 파일 크기 추가 감소
                    if img.mode not in ("L", "1"):
                        img = img.convert("L")
                    img.save(png_path, "PNG", optimize=True)
                    converted += 1
                    if converted % 50 == 0:
                        print(f"  {converted}개 변환 완료...")
                except Exception as e:
                    print(f"  변환 오류 {bmp.name}: {e}")

            # XLS에 없는 곡은 번호만으로 등록
            if num not in songs:
                songs[num] = {"number": num, "title": f"곡 {num}", "lyrics": ""}

    print(f"  변환: {converted}개, 건너뜀(이미 존재): {skipped}개\n")
    return songs


def save_json(songs):
    songs_list = sorted(songs.values(), key=lambda x: x["number"])
    with open(SONGS_JSON, "w", encoding="utf-8") as f:
        json.dump(songs_list, f, ensure_ascii=False, indent=2)
    print(f"songs.json 저장 완료: {len(songs_list)}곡")


if __name__ == "__main__":
    print("=" * 50)
    print("찬미예수 2000 악보 웹사이트 준비 스크립트")
    print("=" * 50 + "\n")

    install_packages()
    songs = read_xls()
    songs = convert_bmp_to_png(songs)
    save_json(songs)

    print("\n✅ 완료!")
    print(f"   images/ 폴더: {len(list(IMAGES_DIR.glob('*.png')))}개 PNG")
    print(f"   songs.json: {SONGS_JSON}")
    print("\n다음 단계: index.html 을 브라우저로 열거나 GitHub Pages에 업로드하세요.")
