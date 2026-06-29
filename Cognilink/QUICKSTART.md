# CogniLink Quick Start Guide

## Installation

### 1. Install dependencies

```bash
cd CogniLink
npm install
```

### 2. Start the development server

```bash
npm run dev
```

The application will start at: http://localhost:5173

### 3. Build the production version

```bash
npm run build
```

The built files will be generated in the `dist` directory.

### 4. Preview the production build

```bash
npm run preview
```

## User Guide

### Add a Bookmark

1. Click the “Add Bookmark” button in the top-right corner.
2. Fill in the bookmark information:：
   - **Title**(required)：Bookmark title
   - **URL**(required)：Website address
   - **Description** (optional)：Bookmark description
   - **Notes** (optional)：Personal notes
   - **Category** (optional)：Select or create a category
   - **Tags** (optional)）：Add tags (press Enter to add)
3. Click “Add” to save.

### Search Bookmarks

1. Enter keywords in the top search bar.
2. The system automatically searches:
   - Title
   - Description
   - Notes
   - URL
   - Tags
3. Results are sorted by relevance.

### Manage Categories

1. Click “Categories” in the sidebar.
2. Click “Add Category” to create a new category.
3. Set the category name, description, color, and icon.
4. Click a category name to filter bookmarks within that category.

### Use Tags

1. Enter tags when adding or editing a bookmark.
2. Click “Tags” in the sidebar to view all tags.
3. Click a tag to filter bookmarks containing that tag.
4. Tags are sorted by usage frequency.

### Favorites and Archive

- **Favorite**：Click the star icon on a bookmark card.
- **Archive**：Click the “Archive” button on the bookmark detail page.
- **Filter**：Use the filter panel to quickly view favorited or archived bookmarks.

### Edit a Bookmark

1. Click a bookmark card to view details.
2. Click “Edit.”
3. Modify the bookmark information.
4. Click “Update” to save.

### Delete a Bookmark

1. Click “Delete” on the bookmark detail page.
2. Confirm the deletion.

## Data Storage

All data is stored locally in the browser using IndexedDB:
- **Database name**: CogniLinkDB
- **Version**: 1
- **Object stores**: bookmarks, categories, tags

## Notes

1. **Data backup:**：Regularly export your data. Clearing browser data will permanently delete all bookmarks.
2. **Browser support**：Latest versions of Chrome, Firefox, or Safari are recommended.
3. **Data migration**：Future version upgrades will handle data migration automatically.

## Troubleshooting

### Issue: Unable to open the database

**Solutions:**：
- Check whether the browser supports IndexedDB.
- Clear the browser cache and try again.
- Check error messages in the browser console.

### Issue: No search results

**Solutions**：
- Verify that the search keywords are correct.
- Try different keywords.
- Check whether the bookmarks were added successfully.

### Issue: Unable to save bookmarks

**Solutions:**：
- Ensure the title and URL are filled in.
- Verify that the URL format is correct.
- Check the browser console for error messages.

## Technical Support

For more information, refer to:：
- README.md - Full documentation
- PROJECT_SUMMARY.md - Project overview
- 浏览器控制台 - Error messages

## Development Information

- **Tech stack**: React 18+, TypeScript, IndexedDB, Vite
- **Number of components**: 30+
- **Lines of code**: ~4,500+
- **Project status**: Core features completed

