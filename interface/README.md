# UI/UX Interface Documentation

The User Interface of OptiLogix Enterprise is built on top of **Streamlit** and enhanced with a custom design system to simulate a high-end corporate SaaS Business Intelligence (BI) dashboard.

## Key Features

1. **Carbon Dark Theme**: Hand-tailored CSS with a curated HSL color palette, utilizing deep slate backgrounds (`#0b0f19`) and vibrant emerald green highlights (`#10b981`).
2. **Glassmorphism KPI Cards**: Dynamic cards with subtle blurs, borders, and shadows that react to hover micro-animations (`transform: translateY(-5px)`).
3. **Responsive Grid Layout**: Utilizing Streamlit columns to adapt to different display widths dynamically.
4. **Interactive GIS Maps**: Renders high-end dark Leaflet maps utilizing `folium` and `streamlit-folium` with real-road polyline layers.
5. **Modern Typography**: Integrated Google Fonts (`Outfit` for base sans-serif styling and `Space Grotesk` for code/data metrics).

## Style Customizations
The styling tokens are managed in `assets/style.css`.
