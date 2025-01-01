from datetime import datetime

def get_email_template(projects):
    """Generate the HTML email template with the given projects."""
    
    # Start with the HTML header and styles
    html = f"""
    <html>
        <head>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6;
                    background-color: #f9fafb;
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                }}
                .project {{ 
                    margin-bottom: 30px; 
                    padding: 20px; 
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    background-color: #ffffff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }}
                .title {{ 
                    color: #2563eb; 
                    font-size: 20px; 
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
                .title a {{
                    color: inherit;
                    text-decoration: none;
                }}
                .title a:hover {{
                    text-decoration: underline;
                }}
                .author {{ 
                    color: #4b5563;
                    margin-bottom: 8px;
                }}
                .growth {{
                    color: #059669;
                    font-weight: 600;
                    margin: 8px 0;
                    font-size: 14px;
                    background-color: #ecfdf5;
                    padding: 4px 8px;
                    border-radius: 4px;
                    display: inline-block;
                }}
                .description {{ 
                    color: #1f2937;
                    margin: 16px 0;
                    line-height: 1.6;
                }}
                .stats {{ 
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    color: #6b7280;
                    font-size: 14px;
                    margin: 12px 0;
                    padding: 8px 0;
                    border-top: 1px solid #f3f4f6;
                }}
                .tags {{
                    margin-top: 8px;
                }}
                .tag {{
                    background-color: #f3f4f6;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #4b5563;
                    margin-right: 6px;
                    margin-bottom: 4px;
                    display: inline-block;
                }}
            </style>
        </head>
        <body>
            <h1>🤗 Rising Stars in Top 500</h1>
            <p>Here are the fastest-growing models among Hugging Face's most-downloaded models as of {datetime.now().strftime('%Y-%m-%d')}:</p>
    """
    
    # Add each project to the template
    for project in projects:
        # Format tags
        tags_html = ""
        if project['tags']:
            tags = project['tags'][:5]  # Take first 5 tags
            tags_html = '<div class="tags">' + ''.join([f'<span class="tag">{tag}</span>' for tag in tags]) + '</div>'
        
        # Format last modified date
        try:
            if isinstance(project['last_modified'], str):
                last_modified = datetime.fromisoformat(project['last_modified'].replace('Z', '+00:00'))
            else:
                last_modified = project['last_modified']
            last_modified_str = last_modified.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            last_modified_str = "Recently"
        
        # Add project section
        html += f"""
            <div class="project">
                <div class="title"><a href="{project['link']}">{project['title']}</a></div>
                <div class="author">by {project['author']}</div>
                {f'<div class="growth">{project["growth"]}</div>' if project.get('growth') else ''}
                <div class="description">{project['description']}</div>
                <div class="stats">
                    <span>❤️ {project['likes']}</span>
                    <span>⬇️ {project['downloads']:,} downloads</span>
                    <span>🕒 Updated: {last_modified_str}</span>
                </div>
                {tags_html}
            </div>
        """
    
    # Close the HTML
    html += """
        </body>
    </html>
    """
    
    return html