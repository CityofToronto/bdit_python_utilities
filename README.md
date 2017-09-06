# Python Utilities

This repository contains utilities to be used/imported in other Big Data Innovation Team projects.

## Add this repository to your Python scripts

In the terminal run:

`python -m site`

This should ouput the contents of `sys.path`, amongst others. You're looking for an entry that ends with `site-packages`. Navigate to that folder.

Create a text file called `python_utilities.pth` inside the `site-packages` folder. And inside it add:
```
C:\path\to\the\bdit_python_utilities\repository\
```

Python will look into folders listed in any `.pth` file in `site-packages` for modules to import.

## How to add modules

You've probably been working on a Python program in one of our project repositories, when you figured out how to make it more generalizable and useful for other projects in our team. [Follow these instructions](http://gbayer.com/development/moving-files-from-one-git-repository-to-another-preserving-history/)

Using `git shell`
```shell
git clone initial_repo/ temp_repo
```

Just to be safe, add `temp_repo` as a repository in Github for Windows and then open `git shell` for that repo. Then:

```shell
git remote rm origin 
git filter-branch --subdirectory-filter folder-to-keep -- --all
```

Now the contents of `folder-to-keep` are in the root of `temp_repo/`. You can attempt further cleaning using some commands [here](https://git-scm.com/docs/git-filter-branch), I just opted to use `git rm` for files that will stay in the original repository. Also make sure to create a folder with `mdkir module_name` and then `git mv stuff_to_keep module_name/`. When all changes are finished, don't forget to commit.

Now navigate to `bdit_python_utilities/` and run:
```shell
git remote add newmodule ../temp_repo
git pull --allow-unrelated-histories newmodule master
git remote rm newmodule
```
And everything should be set to go!
