from exporters.ai_features_ppt import build_ai_features_ppt


def main():
	path = build_ai_features_ppt()
	print(f"Exported features PPT to: {path}")


if __name__ == "__main__":
	main()
