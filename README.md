# Python Utilities

This repository contains utilities to be used/imported in other Big Data Innovation Team projects.

## Add this repository to your Python scripts

In the terminal run:

`python -m site`

This should ouput the contents of `sys.path`, amongst others. You're looking for an entry that ends with `site-packages`. Navigate to that folder.

Create a text file called `python_utilities.pth`. And inside it add:
```
C:\path\to\this\repository\
```

Python will look into folders listed in any `.pth` file in `site-packages` for modules to import.

## How to add modules

You've probably been working on a Python program in one of our project repositories, when you figured out how to make it more generalizable and useful for other projects in our team. [Follow these instructions](http://gbayer.com/development/moving-files-from-one-git-repository-to-another-preserving-history/)