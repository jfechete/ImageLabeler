# Image Labeler
I made this to more easily label images for machine learning projects.  
To use it, run main.py and then select a folder that contains image files and a "config.ini" file in it.

## config.ini
The "config.ini" file can have two sections.  
The first one is required and should be named "labels". Keys can be any name and will represent the label name. Values should be the type of data the key will represent. It currently supports booleans and radio selections. For a boolean, simply set the value to "bool".
For a radio, set it to "radio:{option1},{option2},{option3},{...}".  
The second section is optional, and should be named "hotkeys". Each key there should match a key from the "labels" tab, and the value should be a string of the hotkeys. If a boolean, the string should be a single character. For a radio have the same number of characters as options in the radio. Any that aren't set in this section will be auto-assigned a letter from the left half of a keyboard.  

## output
As images are labeled, if all options have a value then it will be written to a .json file. It will have the label data and have the same name as the image, just suffixed with .json. Once many are labeled, you can also click the button at the bottom to export a .csv file of all the images.  
