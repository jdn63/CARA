import requests
from bs4 import BeautifulSoup
import logging
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        logger.error(f"Error fetching website content: {str(e)}")
        return ""

def get_wi_health_departments():
    """
    Fetch the list of Wisconsin health departments from the official source
    """
    try:
        # DHS Wisconsin Local Health Departments page
        url = "https://www.dhs.wisconsin.gov/lh-depts/index.htm"
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch health departments: Status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract health departments from the page
        departments = []
        
        # Look for tables or lists containing health department information
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if len(cells) >= 2:
                    dept_name = cells[0].get_text(strip=True)
                    county = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    
                    # Only add if we have a department name
                    if dept_name and not dept_name.lower().startswith('name'):
                        departments.append({
                            'name': dept_name,
                            'county': county
                        })
        
        # If no tables found, try lists
        if not departments:
            lists = soup.find_all(['ul', 'ol'])
            for list_elem in lists:
                items = list_elem.find_all('li')
                for item in items:
                    dept_text = item.get_text(strip=True)
                    if dept_text and 'health department' in dept_text.lower():
                        departments.append({
                            'name': dept_text,
                            'county': ""  # County info might not be available in list format
                        })
        
        # Get tribal health centers/departments
        tribal_departments = get_wi_tribal_health_departments()
        if tribal_departments:
            departments.extend(tribal_departments)
        
        return departments
        
    except Exception as e:
        logger.error(f"Error scraping health departments: {str(e)}")
        return []

def get_wi_tribal_health_departments():
    """
    Fetch the list of Wisconsin tribal health departments/centers from the official source
    """
    try:
        # DHS Wisconsin Tribal Health Centers page
        url = "https://www.dhs.wisconsin.gov/tribal-affairs/index.htm"
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch tribal health departments: Status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract tribal health departments from the page
        tribal_departments = []
        
        # Look for content containing tribal health center information
        content_div = soup.find('div', class_='content-block')
        if content_div:
            # Find all headers and lists that might contain tribal health centers
            headers = content_div.find_all(['h2', 'h3', 'h4'])
            
            for header in headers:
                # Check if this header is about tribal health centers
                if any(term in header.get_text().lower() for term in ['health center', 'health department', 'healthcare']):
                    # Get the list that follows this header
                    next_elem = header.find_next(['ul', 'ol'])
                    if next_elem:
                        items = next_elem.find_all('li')
                        for item in items:
                            dept_text = item.get_text(strip=True)
                            if dept_text:
                                # Extract the tribe/nation name from the text
                                parts = dept_text.split(' Health ')
                                tribe_name = parts[0].strip() if len(parts) > 1 else dept_text
                                
                                tribal_departments.append({
                                    'name': tribe_name,
                                    'county': dept_text,
                                    'is_tribal': True
                                })
        
        # If no structured data found, use a hardcoded list based on DHS information
        if not tribal_departments:
            # This list is based on the 11 federally recognized tribes in Wisconsin
            tribal_departments = [
                {'name': 'Bad River', 'county': 'Bad River Health and Wellness Center', 'is_tribal': True},
                {'name': 'Forest County Potawatomi', 'county': 'Forest County Potawatomi Health & Wellness Center', 'is_tribal': True},
                {'name': 'Ho-Chunk Nation', 'county': 'Ho-Chunk Nation Health Department', 'is_tribal': True},
                {'name': 'Lac Courte Oreilles', 'county': 'Lac Courte Oreilles Community Health Center', 'is_tribal': True},
                {'name': 'Lac du Flambeau', 'county': 'Peter Christensen Health Center', 'is_tribal': True},
                {'name': 'Menominee Indian Tribe', 'county': 'Menominee Tribal Clinic', 'is_tribal': True},
                {'name': 'Oneida Nation', 'county': 'Oneida Community Health Center', 'is_tribal': True},
                {'name': 'Red Cliff Band', 'county': 'Red Cliff Community Health Center', 'is_tribal': True},
                {'name': 'Sokaogon Chippewa', 'county': 'Sokaogon Chippewa Health Clinic', 'is_tribal': True},
                {'name': 'St. Croix Chippewa', 'county': 'St. Croix Tribal Health Clinic', 'is_tribal': True},
                {'name': 'Stockbridge-Munsee', 'county': 'Stockbridge-Munsee Health and Wellness Center', 'is_tribal': True}
            ]
            
        return tribal_departments
        
    except Exception as e:
        logger.error(f"Error scraping tribal health departments: {str(e)}")
        # Fall back to hardcoded list if there's an error
        return [
            {'name': 'Bad River', 'county': 'Bad River Health and Wellness Center', 'is_tribal': True},
            {'name': 'Forest County Potawatomi', 'county': 'Forest County Potawatomi Health & Wellness Center', 'is_tribal': True},
            {'name': 'Ho-Chunk Nation', 'county': 'Ho-Chunk Nation Health Department', 'is_tribal': True},
            {'name': 'Lac Courte Oreilles', 'county': 'Lac Courte Oreilles Community Health Center', 'is_tribal': True},
            {'name': 'Lac du Flambeau', 'county': 'Peter Christensen Health Center', 'is_tribal': True},
            {'name': 'Menominee Indian Tribe', 'county': 'Menominee Tribal Clinic', 'is_tribal': True},
            {'name': 'Oneida Nation', 'county': 'Oneida Community Health Center', 'is_tribal': True},
            {'name': 'Red Cliff Band', 'county': 'Red Cliff Community Health Center', 'is_tribal': True},
            {'name': 'Sokaogon Chippewa', 'county': 'Sokaogon Chippewa Health Clinic', 'is_tribal': True},
            {'name': 'St. Croix Chippewa', 'county': 'St. Croix Tribal Health Clinic', 'is_tribal': True},
            {'name': 'Stockbridge-Munsee', 'county': 'Stockbridge-Munsee Health and Wellness Center', 'is_tribal': True}
        ]

def get_wi_health_departments_from_text():
    """
    Process Wisconsin health department listings from raw text
    when direct web scraping is not providing structured data
    """
    try:
        url = "https://www.dhs.wisconsin.gov/lh-depts/index.htm"
        text_content = get_website_text_content(url)
        
        if not text_content:
            logger.error("Failed to fetch health department text content")
            return []
            
        # Process the text content to extract health departments
        # This is a backup method when structured parsing fails
        lines = text_content.split('\n')
        departments = []
        current_county = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains county name
            if "County" in line and "Health Department" not in line and "Public Health" not in line:
                current_county = line
            # Check if line contains health department info
            elif any(term in line.lower() for term in ["health department", "public health", "health services"]):
                dept_name = line
                departments.append({
                    'name': dept_name,
                    'county': current_county
                })
                
        return departments
        
    except Exception as e:
        logger.error(f"Error extracting health departments from text: {str(e)}")
        return []

# NOTE: The Wisconsin DHS respiratory illness HTML scraper that previously
# lived here (get_wi_dhs_respiratory_data, get_county_respiratory_data, and
# their extract_* / calculate_respiratory_risk_score helpers) has been
# removed. CDC NSSP (data.cdc.gov/resource/vutn-jzwm) is the genuine
# primary source for Wisconsin respiratory ED visit surveillance and is
# fetched directly via utils.nssp_respiratory.fetch_nssp_wi_respiratory().
# The same NSSP/ESSENCE feed underlies the WI DHS respiratory dashboards
# the scraper used to read, so going to NSSP directly is more accurate
# and avoids fragile HTML parsing.
