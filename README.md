# Crossword Generator

A Python-based crossword puzzle generator that creates crossword puzzles from word lists and custom configurations.

## Features

- Generate crossword puzzles from word lists
- Support for custom words with high priority
- Configurable board size and layout
- Pre-placed words and block positions
- Multiple solving algorithms (BFS, heuristic BFS, recursive)

## Installation

1. Clone this repository
2. Install required dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Ensure you have a word list file (e.g., `peter-broda-wordlist__scored.txt`)

## Usage

### Basic Usage

Run the crossword generator with the default configuration:

```bash
python crossword.py
```

This will use `puzzle_config.yaml` as the configuration file.

### Custom Configuration

You can specify a different configuration file:

```bash
python crossword.py my_config.yaml
```

### Configuration File Format

The configuration file should be in YAML format with the following structure:

```yaml
# Word list file to use
word_list_file: "peter-broda-wordlist__scored.txt"

# Custom words to add (with high priority)
custom_words:
  - "python"
  - "programming"
  - "algorithm"

# Board dimensions [height, width]
board_shape: [10, 10]

# Pre-placed words [word, row, col, direction]
words:
  - ["python", 0, 0, "across"]
  - ["programming", 2, 0, "down"]

# Required block positions [row, col]
necessary_blockers:
  - [0, 6]
  - [1, 5]

# Optional block positions [row, col]
optional_blockers:
  - [0, 8]
  - [1, 8]
```

### Configuration Options

- **word_list_file**: Path to the word list file (format: word;score)
- **custom_words**: List of words to add with high priority (score 100)
- **board_shape**: Board dimensions as [height, width]
- **words**: List of pre-placed words in format [word, row, col, direction]
- **necessary_blockers**: Required black square positions
- **optional_blockers**: Optional black square positions

### Getting Started

1. Copy the example configuration:
   ```bash
   cp puzzle_config.example.yaml puzzle_config.yaml
   ```

2. Edit `puzzle_config.yaml` with your desired words and layout

3. Run the generator:
   ```bash
   python crossword.py
   ```

4. Check the generated solutions in `solutions.txt`

## File Structure

- `crossword.py` - Main crossword generator script
- `puzzle_config.yaml` - Configuration file (create this from example)
- `puzzle_config.example.yaml` - Example configuration file
- `peter-broda-wordlist__scored.txt` - Word list file
- `solutions.txt` - Generated solutions (created after running)

## Word List Format

The word list file should contain words in the format:
```
word;score
```

For example:
```
python;85
programming;90
algorithm;88
```

## Output

The generator creates a `solutions.txt` file containing all valid crossword solutions found. Each solution includes:
- The crossword grid (with letters and # for blocks)
- The list of words used
- A separator line between solutions

## Troubleshooting

- **Configuration file not found**: Ensure `puzzle_config.yaml` exists or specify the correct path
- **YAML parsing error**: Check the syntax of your configuration file
- **No solutions found**: Try adjusting the word list, custom words, or block positions
- **Missing word list**: Ensure the word list file exists and is in the correct format
