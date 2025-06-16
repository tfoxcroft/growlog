# GrowLog Application Design Rules

## Overview
This document provides design rules for maintaining consistency across the GrowLog application. The application is a simple CRUD web app built with Python (Flask), SQLite, and Bootstrap.

## Core Design Principles
1. **Consistency**: Maintain consistent styling, layout patterns, and interaction patterns across all pages
2. **Simplicity**: Keep interfaces clean and focused on core functionality
3. **Responsiveness**: Ensure all pages work well on mobile and desktop devices

## Layout Rules
- Use Bootstrap container class with max-width: 800px
- All pages extend [`templates/base.html`](templates/base.html) 
- Header contains application title centered at top
- Footer contains copyright notice centered at bottom
- Main content area uses white-space pattern with consistent padding

## CRUD Operation Patterns

### Listing Items
- Page: [`templates/list.html`](templates/list.html)
- Show search bar at top with submit button
- Display "Add New Item" button below search
- List items in cards with name, description, and action buttons
- For each item:
  - Show Edit button (outline secondary style)
  - Show Delete button (outline danger style) with confirmation
- When no items, show friendly message with link to add item

### Adding Items
- Page: [`templates/add.html`](templates/add.html)
- Form with:
  - Name field (text input, required)
  - Description field (textarea)
  - Submit button (primary style)
  - Cancel button (secondary style) that returns to list

### Editing Items
- Page: [`templates/edit.html`](templates/edit.html)
- Pre-fill form with existing values
- Same field structure as Add form
- Submit button labeled "Update Item"

### Viewing Items
- Page: [`templates/view.html`](templates/view.html)
- Display all item details in read-only format
- Show:
  - Item name as heading
  - All fields with labels
  - "Edit" button (outline secondary style)
  - "Back to List" button (secondary style)

### Deleting Items
- Implemented as POST action in list view
- Requires confirmation before deletion
- No dedicated delete page

### Searching
- Implemented in list view
- Preserve search query in input field after search
- Case-insensitive partial match on name field

## Styling Rules
- Use Bootstrap 5.3 classes for all components
- Custom CSS only in [`static/css/styles.css`](static/css/styles.css)
- Color scheme:
  - Primary: Bootstrap default blue (#0d6efd)
  - Secondary: Bootstrap default gray (#6c757d)
  - Danger: Bootstrap default red (#dc3545)
- Buttons:
  - Primary actions: btn-primary
  - Secondary actions: btn-secondary
  - Destructive actions: btn-outline-danger
  - Small buttons: btn-sm

## Code Structure
- Main application: [`app.py`](app.py)
- Models defined in same file (Item class)
- Templates in templates directory
- Static assets in static directory

## Future Development Guidelines
1. When adding new features:
   - Maintain existing layout patterns
   - Use consistent form styling
   - Follow established naming conventions
2. For new pages:
   - Extend base template
   - Use Bootstrap grid system for layout
   - Add custom styles only when necessary
3. For database changes:
   - Use Flask-Migrate for schema updates
   - Preserve existing data structure where possible