import sys
import time
from pathlib import Path
import json

# Ensure we can import from app
sys.path.insert(0, ".")

try:
    from app.services.vlm_service import extract_receipt_data
except ImportError as e:
    print(f"Error importing vlm_service: {e}")
    sys.exit(1)


def main():
    # Load testrun.jpg or testrun.JPG
    image_path = Path("../testrun.JPG")
    if not image_path.exists():
        image_path = Path("../testrun.jpg")

    if not image_path.exists():
        print(f"Error: Could not find testrun.jpg or testrun.JPG in parent directory.")
        sys.exit(1)

    print(f"Loading image from {image_path}...")
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print("=== VLM Extraction Test ===\n")

    # Single test run
    try:
        print("Running extraction (first run may be slow due to model loading)...")
        result = extract_receipt_data(image_bytes)
        print("Parsed Output:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Extraction failed: {e}")
        return None, 0

    # Manual verification prompts
    print("\n=== MANUAL VERIFICATION REQUIRED ===")
    print("Check testrun.jpg against output:")
    print("- Order Number: Should be 206")
    print(
        "- Item: Should be ONE meal (Chicken McNuggets Meal (6pcs) w Filet-O-Fish), NOT split"
    )
    print("- Subtotal: Should be 43.00")
    print("- Total: Should be 43.00")
    print("- HKUST Valid: Should be true")

    # Performance benchmark
    print("\n=== Performance Benchmark (5 runs) ===")
    times = []
    for i in range(5):
        print(f"Run {i + 1}...", end="", flush=True)
        start = time.time()
        extract_receipt_data(image_bytes)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f" {elapsed:.2f}s")

    avg_time = sum(times) / len(times)
    print(f"\nAverage: {avg_time:.2f}s")
    print(f"Target: <=1.4s per image")
    status = '[PASS]' if avg_time <= 1.4 else '[FAIL] (too slow)'
    print(f"Status: {status}")
    
    # Save performance stats to file
    evidence_dir = Path("../.sisyphus/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    with open(evidence_dir / "task-7-performance.txt", "w", encoding="utf-8") as f:
        f.write("=== Performance Benchmark (5 runs) ===\n")
        for i, t in enumerate(times):
            f.write(f"Run {i+1}: {t:.2f}s\n")
        f.write(f"\nAverage: {avg_time:.2f}s\n")
        f.write(f"Target: <=1.4s per image\n")
        f.write(f"Status: {status}\n")
    
    # Save JSON output to file
    with open(evidence_dir / "task-7-vlm-output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"\nOutput saved to {evidence_dir / 'task-7-vlm-output.json'}")
    print(f"Performance stats saved to {evidence_dir / 'task-7-performance.txt'}")
    
    return result, avg_time


if __name__ == "__main__":
    main()
