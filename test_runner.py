import subprocess
import sys
import os

def run_test(task_id, executable):
    test_dir = os.path.join("app", "tasks", f"task_{task_id}", "tests")
    input_file = os.path.join(test_dir, "input.txt")
    expected_output_file = os.path.join(test_dir, "expected_output.txt")

    # Read expected output
    with open(expected_output_file, "r") as f:
        expected_output = f.read().strip()

    # Run the compiled program with the input
    with open(input_file, "r") as input_f:
        process = subprocess.run(
            [executable],
            stdin=input_f,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    # Check output
    if process.returncode != 0:
        return f"Runtime Error:\n{process.stderr}"

    actual_output = process.stdout.strip()
    if actual_output == expected_output:
        return "Test Passed"
    else:
        return f"Test Failed\nExpected: {expected_output}\nGot: {actual_output}"

if __name__ == "__main__":
    task_id = sys.argv[1]
    executable = sys.argv[2]
    print(run_test(task_id, executable))
