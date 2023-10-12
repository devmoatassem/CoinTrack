# CoinTrack
#### Video Demo:  <https://youtu.be/SuzuRXMSvMs>
### Description:
A personal finance tracker built using Python-Flask, HTML, CSS, Bootstrap, and SQLite as the database consists of two main pages. Let's discuss each one in detail.
#### Welcome Page
The personal finance tracker is simply designed with a project tagline and two buttons. Users will be redirected to the welcome page if they're not signed in; otherwise, the default URL will open the dashboard.

On the welcome page, users can navigate to the sign-in and login pages, which are designed with consistency in mind to maintain a unified design theme.
#### Dashboard Page
In the dashboard, there are several sections:

1. "Current Month Expenses," "Income," and "Balance" sections.
2. A single-line graph that provides an annual comparison between expenses and income, offering users a quick insight into their financials over the year.
3. A ledger control feature that allows users to add, remove, and view totals for a particular ledger.
4. At the top header, users can see the current page name and date.
5. There's a side navigation pane where the user's name is displayed at the top. In the center, users can navigate to different pages, and at the bottom, they can sign out.
#### Table Page
The table page offers multiple options, which we can explore one by one:

1. Users can add transactions using a form that takes input for date, income, expenses, ledger, and description. The "Add" button calls a special route in the Flask backend, which utilizes the Python sqlite3 library to INSERT the transaction into the transaction table.

2. At the bottom of the page, there's a table displaying all the entries in the transaction table, with the latest entry at the top.

3. Each entry in the table can be deleted or edited using buttons located at the left-most side of the rows.

4. Users can search through entries using a search bar located in the header of the table.

5. The filter feature can be accessed by clicking the filter button at the top left of the table. If a filter is already applied, users will see a "Remove Filter" button.

6. In the filter, users can apply various filtering options to the entries in the table, including By Month, By Year, By Ledger, and By Transaction Type. Users can apply these filters individually or in combination.

These options provide users with comprehensive control and flexibility in managing and viewing their financial transactions.

#### About Page
This page includes a brief introduction and outlines my motivation behind the project.

#### Contact Page
This page contains contact information for obtaining assistance with deployment issues and for businesses interested in implementing the project with custom modifications.

 # Credits
- CS50 https://cs50.harvard.edu/x
- https://uiverse.io/forms
- https://cssbuttons.app/ Nice CSS codes for Different components
- https://bgjar.com/ SVG background generator with different templates
- https://bennettfeely.com/clippy/  create clipping masks of different shapes in CSS (particularly useful for using an image putting an overlay of some text over it)
- https://neumorphism.io/#e0e0e0 CSS codes for shaodows, edges etc
- https://ui.glass/generator/  & https://css.glass/ Glass like background effect generator
- https://www.blobmaker.app/ make different shapes using CSS, different blobs
- https://products.ls.graphics/mesh-gradients/ Generate custom Mesh Gradients with custom color and custom patterns
- https://animate.style/ Animate CSS
- https://fontawesome.com/ For ICONS
- https://getbootstrap.com/docs/5.3/getting-started/introduction/ Bootstrap 5.3
# Contact
https://moatassam.com/#contact
