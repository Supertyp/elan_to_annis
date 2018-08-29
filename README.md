# elan_to_annis
convert elan files into relANNIS format

a) create a config file
1. put all ELAN files (.eaf) into a folder
2. configure the input path in the config file maker to point to that folder
3. configure the output path to where you want the config file

b) edit config file
1. look at the config file and choose/change the mainText tier for each file. 
   You can add a second and third tier name to the list to import a dialog or conversation
2. chech the spelling you want in each of the replacement dictionaries.
    NOTE: if you change the spelling of a tier which is also the main text, you also 
          have to change the spelling in the mainText list.
3. add tiers you want ignored to the delete list

c) run the elan_to_annis script
1. pick the config file you want to use
2. set the path to the .eaf files
3. set the path to the output folder
4. run the script
5. zip up the output folder for ANNIS import

That should be it!

