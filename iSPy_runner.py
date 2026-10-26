"""
Main script to construct figures and find clusters from ilastik data.
Based on the iSPY (Inferring Spatial Ploidy) framework.
"""


from pathlib import Path
import sys
import matplotlib.pyplot as plt

# Dynamic project paths
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.basics.Character_Class as Class
from tools.basics.Plotting_Definitions_Class import Plot
from tools.curve_fitting.Curve_Fitting_SKLearn import Full_CurveFits

try:
    from tools.basics.Prediction_Definitions_Class import PredictionImage
except ImportError:
    PredictionImage = None

plt.rcParams['font.family'] = 'sans-serif'

## this allows interactive plots
#%matplotlib notebook

## If you do not want interactive plots, please change here.
#%matplotlib inline

# Here is where you can start changing things!

#############################
### Create your directory ###
#############################

### Files will be saved in a "Results" folder. Please define a subfolder here to save this run of the code.
## i.e., your files will be saved in "Results/your_folder_name".

exp_str = 'First_Experiment_With_Objects'

#############################################
####### Input Variables of Interest #########
#############################################

# Which two characteristics do you want to plot? Please input the columns you would like to compare.
# Look at your CSV file to find the relevant columns.
# Note that ilastik has changed the column names slightly in the past, so you may have to
# change certain words and capitalization.

# The characteristics below are from ilastik version 1.4.0, but inputting any CSV file will work.

# Note that Char1 will be the x-axis, and Char2 will be the y-axis.

#Example: Comparison between Size and Total Intensity
Char1_Name = "Size in pixels"
Char2_Name = "Total Intensity in neighborhood_1"

#Char1_Name = ''
#Char2_Name = ''

# If you are in this notebook, you have preclassified objects for your segmentation (e.g., nuclei and stomata).
# Please identify the column in the CSV file which represents this classification and
# input it as the variable "Object_Name".
# If you do not have these columns or do not have preclassified objects, please use the other jupyter notebook.

#Example:
Object_Name = 'User Label'

######################################################
####### Normalization and Scaling Parameters #########
######################################################

# If you would like to normalize the data, please select from the options here. 'None' does nothing.
# e.g. Take the total intensity and divide all values by the maximum of all intensities

Char1_Norm = 'Median' #Choices: 'None', 'Max', 'Median', 'Mean'
Char2_Norm = 'Median' #Choices: 'None', 'Max', 'Median', 'Mean'

# If you selected 'Max' for the norm, please input a number here, which we will denote as K.
# K will correspond to the highest K numbers, which we will then take the mean of. This mean
# will then be utilized for normalization. Ex: if you input 1, we will take the maximum value
# and divide this by all values. If you input 5, we will take the highest 5 values, find the mean
# and then divide all values by this mean.

Char1_NormAtt = 5 #Choices: 'None', 'Max', 'Median', 'Mean'
Char2_NormAtt = 5 #Choices: 'None', 'Max', 'Median', 'Mean'

# If you would like to scale the axes, please select from the options here.
# This will create graphs with, e.g., a log 10 - log 2 scale, linear/log scale, etc.

Char1_Scale = 'Log' #Choices: 'Linear', 'Log'
Char2_Scale = 'Log' #Choices: 'Linear', 'Log'

# If you have selected 'Log' above, which base would you like to scale your plot with?
# Note that this does nothing with 'Linear' selected above.

Char1_Base = 2
Char2_Base = 2

# Now we will construct your bins of the histogram.
# You can either do this by inputting the number of bins you would like
# or how large you want your bin sizes to be. Please note the following:
# If Char1_BinType = 'Number', Char1_BinValue will be the number of bins you would like (must be an integer)
# If Char1_BinType = 'Width', Char1_BinValue will be the width of your bins.
# This is not allowed if Char1_Scale = "Log"

Char1_BinType = 'Number' #Choices: 'Number' or 'Width'
Char1_BinValue = 60 #Must input an integer or float.

Char2_BinType = 'Number' #Choices: 'Number' or 'Width'
Char2_BinValue = 60 #Must input an integer or float.


# Should the histograms generated be scaled so that the area is equal to 1?
# If so, please change denChar1 or 2 to True.
# Please note that using denChar = True may cause issues if the values of your
# characteristics/variables are too high. We recommend using False initially if this is the case.
# Please see https://numpy.org/doc/stable/reference/generated/numpy.histogram.html for more detail.

denChar1 = True
denChar2 = True

######################
####### Files ########
######################

# Input your files here in this array.
# As well, please put the legends you would like to use for each of the files in the scatter plot.
# These legends will be also used as proxies in case you would like to output specific files later on.

## Example
#Files = ['file1.csv','file2.csv']
#Legends = ['File 1', 'File 2']

#Files = []
#Legends = []

### Please see below for an example of how to do this via a for-loop

#PWD = '/content/drive/MyDrive/ispy-inferring-spatial-ploidy/Data/Cardiomyocyte_Data/Left Atrium/ilastik/'
# Data file paths (relative to repository data folder)
DATA_DIR = REPO_ROOT / "Data" / "Cardiomyocyte_Data" / "Left Atrium" / "ilastik"

Files = []
Legends = []
for j in [1, 4]:
    Files.append(str(DATA_DIR / f"Data_Table_{j}.csv"))
    Legends.append(f"Data_Table {j}")

### Optional: Raw Image Files ###

# If you would like to use your predictions to output TIFF/H5 files that show your predicted classes,
# please put the list of raw data files (either TIFF or H5) below.
# Note that this only works if you have output the Object Identities file from ilastik or
# a TIFF/H5 file which identifies each voxel with the corresponding object identity:
# (e.g., Voxel z = 15, y = 234, x = 221 is part of labelled nuclei 18).
# Please change Prediction_Outputs to be equal to 1 if you would like this.
# By default, if dims > 2, we will perform a projection and output a 2D image. If you would like
# to have a colored 3D file which you can visualize with other types of software (e.g., blender, Fiji, etc)
# put Prediction_Outputs_3D equal to 1
# Column_ID_Label is the column in the CSV file that represents the labels of each nuclei in the RawImageFiles. For ilastik, this would be 'labelimage_oid'
# Note that this process may take a while.

Prediction_Outputs = 0
Prediction_Outputs_3D = 0
RawImageFiles = []
Column_ID_Label = ''


##############################
#### Plotting Preferences ####
##############################

dark = 1 # For a plot with a white background, please put 0. For a black plot, please put 1.

# If you would like to put in your own strings for the x and y-labels, do so here.
# If left blank, they will be generated automatically (using the characterstics and the norm)

#Examples
Char1_Label = r'Volume ($\mu m^3$)' #For Char1.
Char2_Label = 'Total Intensity' #For Char2.

#Char1_Label = '' #For Char1.
#Char2_Label = '' #For Char2.


# Do you need to scale variables by your pixel size?
# ilastik does not consider pixel/voxel size for volume.
# So you need to manually provide the pixel/voxel size.

dims = 3 #If you only have 2 dimensions, please change it here. Then, Voxel_z won't be considered.
Voxel_x = 1
Voxel_y = 1
Voxel_z = 1
Voxels = [Voxel_x,Voxel_y,Voxel_z]

# Do you need to set a threshold to filter data?
# Please change Low/High_Threshold_YN1/2 = 1 if you want to filter your data with a low or high threshold.
# Then, correspondingly, change the Low/High_Threshold1/2 parameter to the value you would like to set
# as the lower or upper bound. As an example, with Low_Threshold_1 = 1 and Low_Threshold1 = 100, this means
# we will filter out all objects which have a value less than 100 for Characteristic 1.

# Characteristic 1 #
Low_Threshold_YN1 = 0
Low_Threshold1 = 0
High_Threshold_YN1 = 0
High_Threshold1 = 0

# Characteristic 2 #
Low_Threshold_YN2 = 0
Low_Threshold2 = 0
High_Threshold_YN2 = 0
High_Threshold2 = 0

# What colors do you want to use for your plots? Please put them here and in the order you would like them.
# Note that colorsFiles represents different colors for each file.
# colorsObj represents different colors for different pre-classified objects
# (e.g., nuclei and stomatal guard cells)

# colorsFiles = ['#648FFF','#785EF0','#DC267F','#FE6100','#785EF0'] # IBM Colorblind Scheme

# Colorblind Schemes using Wong (2011) Color Scheme (https://www.nature.com/articles/nmeth.1618)
# white background
# colorsFiles = ['#E69F00','#56B4E9','#009E73','#F0E442','#0072B2','#D55E00','#CC79A7','#FFFFFF']
# dark background
# colorsFiles = ['#E69F00','#56B4E9','#009E73','#F0E442','#0072B2','#D55E00','#CC79A7','#000000']

# Colorblind friendly pallete suggested by https://personal.sron.nl/~pault/
colorsFiles = ['#882255','#AA4499','#CC6677','#DDCC77','#88CCEE','#44AA99','#117733','#332288']

# Colors for Objects
colorsObj = ['#E69F00','#56B4E9','#009E73','#F0E442','#0072B2','#D55E00','#CC79A7','#FFFFFF']

# For the prediction colorscheme, please select a colormap.
# This will only be used to deliniate the predictions from the curve fitting
# and it will be used for coloring your segmentations, if you chose to use that feature.
# See https://matplotlib.org/stable/users/explain/colors/colormaps.html for a list of colormaps

cmap = 'Set3'

#Markers for the scatter plots. Please change them if necessary.
markers = ['o','d','^','s','P','x']
markersize = 10

########################
### What should run? ###
########################

# In this section, please select what parts of the code should run, and - if necessary -
# the proper parameters for your choices


### General scatter plot and histograms
# By default, this code saves a plot which has a scatter plot of the two characteristics chosen,
# and their representative histograms on the x- and y- axes respectively


# Do you want to save these histograms individually as well? If so, put 1. If not, put 0.
indvplot = 1

# Would you like to save the raw scatter plot data generated as a CSV and Numpy file? If so, put 1. If not, put 0.
save_data = 1

# Would you like to generate a ReadMe file with relevant data about your plots? If so, put 1. If not, put 0.
readme = 1

# What file types do you want to save your images as? The options are PNG, PDF, and SVG.
# You can save all three at the same time.

pngs = 1 # Make 1 if you want to save images as PNGs
pdfs = 0 # Make 1 if you want to save images as PDFs
svgs = 0 # Make 1 if you want to save images as SVGs

#####################
### Curve Fitting ###
#####################

# Would you like to perform curve fitting for your singular characteristics? If so, put 1. If not, put 0.
curvefit_1d = 1

#### If you put curvefit_1d = 1, please fill out the following information ####

## For 1D Curve Fitting ##

# We will assume a normal distribution for your peaks to identify them. If this is not the case,
# you may have to generate your own code. Note that this code already takes
## into account logarthmic scaling with the gaussians, if you have chosen that.

# How many peaks do you want to assume for your distribution? Please put in the range of number of peaks
# you would like to search for. We will output several important plots, including the AIC and BIC values
# which we use to find the best fit. We recommend putting a range of values here so you can see the minimum
# AIC and BIC levels.

LowN1d = 6
HighN1d = 6

# Do you want to use AIC or BIC levels? Or both?
AIC = 1
BIC = 1

# How many histograms and curve fits would you like to plot? The number you choose below will
# output that many plots. For instance, putting numplots = 3 will output the 3 best fit plots using
# both the AIC and the BIC as a metric to determine best fit.

numPlots = 1

## For 2D Curve Fitting ##

# Would you like to perform curve fitting for your 2d plot? If so, put 1. If not, put 0.

curvefit_2d = 1

# How many clusters/peaks do you want to assume for your distribution? Please note that for each N, we will output
# 4 files, as we will find the best 2D Gaussian Fit using 4 different covariance types.
# See https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html for more info

LowN2d = 5
HighN2d = 5

###########################################
############## MAIN SCRIPT ################
###########################################

### Please do not change anything below here unless you want to modify the code for your purposes!

def main():
    Char1 = Class.Characteristic(
        Char1_Name, Char1_Norm, Char1_NormAtt,
        Char1_Scale, Char1_Base,
        Char1_BinType, Char1_BinValue,
        Char1_Label, denChar1, 1,
        Low_Threshold_YN1, Low_Threshold1,
        High_Threshold_YN1, High_Threshold1, RawImageFiles, Column_ID_Label
    )

    Char2 = Class.Characteristic(
        Char2_Name, Char2_Norm, Char2_NormAtt,
        Char2_Scale, Char2_Base,
        Char2_BinType, Char2_BinValue,
        Char2_Label, denChar2, 2,
        Low_Threshold_YN2, Low_Threshold2,
        High_Threshold_YN2, High_Threshold2, RawImageFiles, Column_ID_Label
    )

    PlotScheme = Class.Plotting(
        colorsFiles, colorsObj, cmap, markers, markersize, indvplot, AIC, BIC, save_data,
        readme, pngs, pdfs, svgs, dark, exp_str, 1, Object_Name
    )

    Plot(Files, Legends, Char1, Char2, dims, Voxels, PlotScheme)

    Full_CurveFits(
        Char1, Char2, numPlots,
        curvefit_1d, LowN1d, HighN1d,
        curvefit_2d, LowN2d, HighN2d,
        PlotScheme
    )

    if Prediction_Outputs == 1:
        if PredictionImage is not None:
            PredictionImage(RawImageFiles, Column_ID_Label, PlotScheme, Char1, Char2, dims, Voxels, Prediction_Outputs_3D)
        else:
            print("PredictionImage module not available.")

if __name__ == "__main__":
    main()
