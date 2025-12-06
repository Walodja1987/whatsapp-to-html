# Contributing to WhatsApp-To-HTML

Thank you for your interest in contributing to WhatsApp-To-HTML! This document provides guidelines and instructions for contributing to the project.

## How to Contribute

There are many ways to contribute to this project:

- 🐛 **Report bugs** by opening an issue
- 💡 **Suggest new features** by opening an issue
- 🔧 **Fix bugs** or **implement features** by submitting pull requests
- 📝 **Improve documentation** (README, code comments, etc.)
- 🎨 **Enhance styling** (CSS improvements, UI/UX enhancements)
- 🌍 **Add language support** (new languages, date formats, etc.)
- 🧪 **Test the tool** with different WhatsApp exports and report issues

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Git
- A WhatsApp chat export for testing (optional, but recommended)

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/whatsapp-to-html.git
   cd whatsapp-to-html
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guidelines
  - Use 4 spaces for indentation (no tabs)
  - Maximum line length: 100 characters (soft limit)
  - Use descriptive variable and function names
  - Add docstrings for functions and classes
  - Keep functions focused and reasonably sized

- **CSS**: Follow consistent formatting
  - Use 2 spaces for indentation
  - Group related styles together
  - Use CSS custom properties (variables) from `:root` when possible
  - Add comments for complex styling logic

### Testing Your Changes

Before submitting a pull request, please test your changes:

1. **Test with a real WhatsApp export**:
   - Export a chat from WhatsApp (with and without media)
   - Run the script with your test data
   - Verify the HTML output looks correct
   - Check that images, videos, and other media load properly
   - Test with different languages if possible

2. **Test edge cases**:
   - Empty messages
   - Very long messages
   - Messages with special characters
   - Different date formats
   - System messages

3. **Test browser compatibility**:
   - Open the generated HTML in different browsers (Chrome, Firefox, Safari, Edge)
   - Check responsive design on mobile devices (if applicable)

### Project Structure

```
whatsapp-to-html/
├── convert_whatsapp_to_html.py  # Main conversion script
├── style.css                     # CSS styling
├── background.jpg               # Background image (optional)
├── README.md                    # Project documentation
├── CONTRIBUTING.md             # This file
└── .gitignore                  # Git ignore rules
```

## Submitting Changes

### Pull Request Process

1. **Update your fork** with the latest changes from the main repository:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/whatsapp-to-html.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Make your changes** on your feature branch

3. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git add .
   git commit -m "Add support for Portuguese language"
   ```
   
   Commit message guidelines:
   - Use present tense ("Add feature" not "Added feature")
   - Be specific and concise
   - Reference issue numbers if applicable: "Fix #123: Handle empty messages"

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** on GitHub:
   - Provide a clear title and description
   - Explain what changes you made and why
   - Reference any related issues
   - Include screenshots if you changed the UI/styling
   - Mention any testing you've done

### Pull Request Checklist

Before submitting, make sure:

- [ ] Your code follows the project's style guidelines
- [ ] You've tested your changes with real WhatsApp exports
- [ ] You've tested with different languages (if applicable)
- [ ] The HTML output is valid and displays correctly
- [ ] You haven't introduced any breaking changes (or documented them if necessary)
- [ ] Your commit messages are clear and descriptive
- [ ] You've updated documentation if needed (README, comments, etc.)

## Areas for Contribution

### High Priority

- **Language Support**: Add support for more languages (Russian, Chinese, Japanese, Arabic, etc.)
- **Date Format Support**: Improve date parsing for various regional formats
- **Bug Fixes**: Fix any issues reported in the issue tracker
- **Testing**: Test with different WhatsApp export formats and versions

### Medium Priority

- **UI/UX Improvements**: Enhance the chat interface design
- **Accessibility**: Improve accessibility features (keyboard navigation, screen readers, etc.)
- **Performance**: Optimize for very large chat files
- **Documentation**: Improve README, add examples, create tutorials

### Nice to Have

- **Additional Features**: 
  - Search functionality in the HTML output
  - Export to PDF
  - Dark mode toggle
  - Custom themes
- **Code Quality**: Refactoring, code organization improvements
- **Error Handling**: Better error messages and handling

## Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - Python version
   - Operating system
   - WhatsApp export format (iOS/Android, with/without media)
   - Language of the chat export
6. **Screenshots/Error Messages**: If applicable
7. **Sample Data**: If possible, provide a minimal example that reproduces the issue (remove personal information!)

## Suggesting Features

When suggesting features, please include:

1. **Use Case**: Why is this feature useful?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Any alternative solutions you've considered
4. **Additional Context**: Screenshots, mockups, or examples

## Code Review

All pull requests will be reviewed. Feedback may include:

- Code style and formatting
- Logic and implementation
- Testing requirements
- Documentation updates

Please be open to feedback and willing to make changes. The goal is to maintain code quality and ensure the tool works well for everyone.

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the `question` label
- Check existing issues and discussions

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to WhatsApp-To-HTML! 🎉

