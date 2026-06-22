from html.parser import HTMLParser

class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.current_tag = None
        self.text_accumulator = []
        self.context_stack = []

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attr_dict = dict(attrs)
        if tag in ["input", "textarea", "button", "select"]:
            self.inputs.append({
                "tag": tag,
                "type": attr_dict.get("type", ""),
                "name": attr_dict.get("name", ""),
                "id": attr_dict.get("id", ""),
                "placeholder": attr_dict.get("placeholder", ""),
                "value": attr_dict.get("value", ""),
                "accept": attr_dict.get("accept", ""),
                "class": attr_dict.get("class", ""),
                "context": "".join(self.text_accumulator[-100:]).strip()
            })
        self.context_stack.append((tag, attr_dict))

    def handle_endtag(self, tag):
        if self.context_stack:
            self.context_stack.pop()

    def handle_data(self, data):
        clean_data = data.strip()
        if clean_data:
            self.text_accumulator.append(clean_data + " ")
            if len(self.text_accumulator) > 500:
                self.text_accumulator.pop(0)

def main():
    with open("debug_test_single.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = FormParser()
    parser.feed(html_content)

    print("--- File Inputs Found ---")
    for inp in parser.inputs:
        if inp['tag'] == 'input' and inp['type'] == 'file':
            print(f"Tag: {inp['tag']} | Type: {inp['type']} | Name: {inp['name']} | ID: {inp['id']} | Class: {inp['class']}")
            print(f"  Placeholder: {inp['placeholder']} | Value: {inp['value']} | Accept: {inp['accept']}")
            print(f"  Recent Text Context: {inp['context'][-150:]}")
            print("-" * 50)

if __name__ == "__main__":
    main()
