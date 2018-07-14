# FileManager
FileManager with logging and syncing options

# Terminal command line

## List commands
> **help** or **h**

List and explainations of all commands

## Write to log
> **log**  
> Enter name of log file:

Commit the changes to the log file. File path and hash stored in the format
- > **<File_path>** *<File_hash>*

## Compare against log
> **compare**  
> Enter name of log file:

Run a comparison against the log to find which files are new, updated, deleted or renamed

## Sync directories
> **sync**  
> Enter *Source* directory path:  
> Enter *Destination* directory path:


Sync the files between a source and destination directory. Use ~ to reference the current working directory.

For a local subdirectory *Temp*
- > Enter *Source* directory path:  ~/Temp

## Change options
> **opt** <var_name> val1[,val2]*

Use opt to list and change file manager options

## Delete
> **del**  
> Enter name of log file:

Delete the existing log file

## Quit
> **quit** or **q**

Exit the program
