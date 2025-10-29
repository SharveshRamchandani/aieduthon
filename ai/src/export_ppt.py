import sys
from exporters.ppt_exporter import PPTExporter


def main():
	if len(sys.argv) < 2:
		print("Usage: python export_ppt.py <deck_id> [output_dir]")
		sys.exit(1)
	deck_id = sys.argv[1]
	output_dir = sys.argv[2] if len(sys.argv) > 2 else "..\\..\\out"

	exporter = PPTExporter()
	path = exporter.export_deck(deck_id, output_dir)
	print(f"Exported PPTX to: {path}")


if __name__ == "__main__":
	main()
