# GeLaP Dataset converter for NILMTK
The repository with the complete information of this dataset can be found at: https://mygit.th-deg.de/tcg/gelap .

## Download
The data is downloaded from the gitlab repository. For this, it is recommended to use the option to download the repository in zip format (or by accessing this link: https://mygit.th-deg.de/tcg/gelap/-/archive/master/gelap-master.zip).

Once the gitlab zip is downloaded, unzip the folder it contains, and that will be the input for the converter.

## Converter
The converter follows the usual format of the other NILMTK converters. For more details go to the NILMTK repository: https://github.com/nilmtk/nilmtk

## Data converted
The converted h5 file has the data for the 20 houses, with 10 appliances each.
The sampling rate is 1 sample per second for the aggregate measurement, and on average one sample every 0.28 seconds for individual devices.

Some notes that differentiate the converted file from the original data:
- The power of the whole house (site_meter in NILMTK) is in elec 11. This differs from what is usual in other datasets, but it was decided this way so as not to have to modify all the IDs of the individual appliances.
- In the original dataset we have the data of the 3 phases of the home, in the converted h5 we only have the sum of the phases.
- The timestamp of individual devices corresponds to time_reply (in other words, no time_request information is saved)
- Some (few) devices cannot be assigned to some of the valid device types in nilm_metadata, so they are assigned the unknown type.

## Authors
The author of this converter is:
- Mariño, Camilo
  
The authors of the dataset are:
- Wilhelm, Sebastian
- Jakob, Dietmar
- Kasbauer, Jakob
- Ahrens, Diane
