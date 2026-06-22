from html.parser import HTMLParser

class DOMParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.path = []
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.path.append(tag)
        attr_dict = dict(attrs)
        self.elements.append({
            "type": "start",
            "tag": tag,
            "attrs": attr_dict,
            "path": list(self.path),
            "text": ""
        })

    def handle_endtag(self, tag):
        if self.path:
            self.path.pop()
        self.elements.append({
            "type": "end",
            "tag": tag
        })

    def handle_data(self, data):
        if self.elements and self.elements[-1]["type"] == "start":
            self.elements[-1]["text"] += data.strip()

def main():
    try:
        with open("debug_predraft_new.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        with open("debug_test_single.html", "r", encoding="utf-8") as f:
            html = f.read()
            
    parser = DOMParser()
    parser.feed(html)
    
    print("--- Searching for labels and their nearest inputs ---")
    for idx, el in enumerate(parser.elements):
        if el["type"] == "start" and el["text"]:
            txt = el["text"].strip()
            if any(k in txt.lower() for k in ["judul", "artis", "artist", "genre", "language", "bahasa"]):
                print(f"Index: {idx} | Tag: {el['tag']} | Text: '{txt}' | Path: {el['path']}")
                # Look ahead for inputs
                for j in range(idx + 1, min(idx + 50, len(parser.elements))):
                    target = parser.elements[j]
                    if target["type"] == "start" and target["tag"] == "input":
                        print(f"  -> Found input: {target['attrs']}")
                        break

if __name__ == "__main__":
    main()
