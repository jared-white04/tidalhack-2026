# Dashboard Structure Guide

## Overview
The app has been restructured into a multi-page dashboard with sidebar navigation.

## Pages

### 1. Home Page (`/`)
- Hero image with gradient fade
- Title: "Pipeline Data Analysis"
- Two action buttons:
  - **Get Started** - Navigate to Create New Analysis
  - **Load Analysis** - Navigate to Load Analysis (placeholder for now)

### 2. Create New Analysis (`/new-analysis`)
- File upload interface
- List of uploaded files
- "Run Analysis" button (when files are uploaded)
- "Load Test Data" button for testing

### 3. Analysis Page (`/analysis`)
- Pipeline visualization (segment viewer)
- Results table with sorting/filtering
- "New Analysis" button to start over
- Only accessible after running analysis or loading test data

### 4. Load Analysis (`/load-analysis`)
- Placeholder page for future backend integration
- Will display saved analyses once backend is ready

## Navigation

### Sidebar
- Retractable sidebar (click arrow to collapse/expand)
- Menu items:
  - Home
  - Create New Analysis
  - Load Analysis
- Active page is highlighted
- Hover effects on menu items

## Routing
Uses React Router for navigation:
- `BrowserRouter` wraps the entire app
- `Routes` and `Route` components define pages
- `useNavigate` hook for programmatic navigation
- `useLocation` for accessing route state

## Data Flow

### Creating New Analysis:
1. User uploads files on `/new-analysis`
2. Clicks "Run Analysis" or "Load Test Data"
3. Navigates to `/analysis` with results in route state
4. Results displayed in visualization and table

### Navigation State:
- Analysis results passed via `location.state.results`
- Test mode flag passed via `location.state.testMode`
- If no results, redirects back to `/new-analysis`

## Color Customization
All colors still controlled by `client/src/styles/colors.js`:
- Sidebar backgrounds
- Hero gradient
- Button colors
- Text colors
- All existing color options

## Components

### New Components:
- `Sidebar.jsx` - Retractable navigation sidebar
- `HomePage.jsx` - Landing page with hero
- `NewAnalysisPage.jsx` - File upload page
- `AnalysisPage.jsx` - Results display page
- `LoadAnalysisPage.jsx` - Placeholder for saved analyses

### Existing Components (unchanged):
- `FileUpload.jsx` - File upload interface
- `PipelineVisualizer.jsx` - Segment visualization
- `ResultsTable.jsx` - Data table with sorting/filtering

## Future Backend Integration

### Save Analysis Feature:
When backend is ready, add:
1. "Save Analysis" button on Analysis page
2. POST to `/api/analysis/save` with results
3. Update Load Analysis page to fetch saved analyses
4. Display list of saved analyses with metadata
5. Click to load and view previous analysis
