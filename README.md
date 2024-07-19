# Angel Food

## A Restaurant Review Site
This is a website designed to demonstrate my ability to use databases, specifically MongoDB. It is a restaurant review website aimed at my local area of Angel, Islington, and is designed to be used by anyone locally. It has functionality for desktop, but primarily it is envisioned as something used on a smartphone, and includes the ability to add a picture taken by a smartphone camera.

## Concept
There are a great many review websites, and a great many ways to find local eateries or cafes. I make no claims to have invented something truly innovative, but I have certainly created something that is personal to me and to the people I live near. Angel has a great many places to eat and drink, and I wanted to call that out as well as demonstrating that I can use databases.

## User Story
As a user, I want:
+ An app that showcases local food and drink
+ Strong visual style
+ CRUD functionality for places
+ To be able to see places I have submitted
+ Search ability

As an admin, I want, in addition to the previous points:
+ CRUD functionality for cuisine types

## Features and Wireframe
This site comprises several pages linked together with Jinja templating. Common features on each page are the header and footer. The header changes depending on whether you are logged in or out, and whether you are an admin or not.

The images presented here are not final, and are indicative of what a user might see at the point in prototyping that this section of the Readme was written. Colours and designs are not final and are subject to change after prototyping and user testing.

### Main Page
![name of page](readme_docs/prototype/link.png "name of page")

## Upcoming features
+ Google Maps integration - I would like to add the ability to select the place you are reviewing on Google Maps and either link to the Maps app on a phone or have a map onscreen.

## Technology
+ This website was made in its entirety using Gitpod Workspaces
+ Databasing is provided by MongoDB
+ Deployment is from Heroku
+ Images are handled by Cloudinary
+ Wireframe and prototyping images were made in Figma
+ Additional software used to create this website include Photoshop for image editing and Firefox for previewing, inspecting and bug testing

## Testing
### Test Case: First test case name

### Bugs discovered
+ Properly aligning icons in buttons proved to be a challenge, and also to the 'takeaway' toggle. I ended up having to provide some very specifically-targeted CSS for the takeaway toggle
+ The default text on the 'create place' interface is in three different types of grey - black for the dropdowns, light grey for the image, and mid-grey for the remaining fields. Despite extensive effort, I've not been able to change this.

## Code validation

### Lighthouse Report:

### <a href="https://jshint.com/" target="_blank">JSHint</a>

## Supported Screens and Browsers
+ This website works in any browser and at any screen size, from desktop down to smart phones.
+ It has been developed and tested for Firefox, and smaller screen sizes have been simulated with Firefox's Inspect tool. Sample screens of all currently-available smart phones have been tested through Firefox's Inspect tool. It has also been tested natively on a Pixel 7a device and a Pixel 6 Pro.

## Deployment
This website has been deployed on Heroku, the deployment for which is available at https://angel-food-3a8bebdae07e.herokuapp.com/. It was developed using the Code Institute full template repository, available at Github.

To view the deployment on Heroku:

+ Navigate to https://angel-food-3a8bebdae07e.herokuapp.com/

To clone the repository from Github in your editor of choice:

+ First, open your terminal.
+ Change the current working directory to the location where you want the cloned directory.
+ Input: ```bash
+ Input: cd path/to/your/directory (ensure you change the directory to whatever you want to clone the repository)
+ Clone the repository by running: git clone https://github.com/stevecook23/angel-food.git
+ Change directories into the cloned repository: cd angel-food

Now you have a copy of the source code and can start to work on it.

## Credits
### Text Content
Text is provided by users of the site

### Media
#### Readme Images

#### Game Images