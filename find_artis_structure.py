def main():
    try:
        with open("debug_predraft_new.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        with open("debug_test_single.html", "r", encoding="utf-8") as f:
            html = f.read()

    # Let's find "Artis utama" and print ~2000 characters around it
    idx = html.find("Artis utama")
    if idx == -1:
        print("Could not find 'Artis utama'")
        return

    print("Found 'Artis utama' at index:", idx)
    print("--- HTML context around 'Artis utama' ---")
    start = max(0, idx - 200)
    end = min(len(html), idx + 2000)
    print(html[start:end])
    print("------------------------------------------")

if __name__ == "__main__":
    main()
