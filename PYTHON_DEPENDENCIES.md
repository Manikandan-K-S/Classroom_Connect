# Classroom Connect - Python Dependencies Documentation

## Overview
This document provides detailed information about all Python packages used in the Classroom Connect project.

---

## Core Framework (Django Stack)

### Django==5.2.5
- **Purpose**: Main web framework
- **Usage**: Backend server, ORM, templating, admin interface
- **Key Features**: 
  - User authentication
  - Database migrations
  - Template rendering
  - URL routing
  - Session management

### djangorestframework==3.14.0
- **Purpose**: RESTful API framework
- **Usage**: API endpoints for quiz data, student performance
- **Key Features**:
  - Serializers for model data
  - API views and viewsets
  - Permissions and authentication
  - Browsable API interface

---

## Real-time Communication

### channels==4.3.1
- **Purpose**: WebSocket and async support for Django
- **Usage**: Real-time quiz updates, live notifications
- **Key Features**:
  - WebSocket consumers
  - Channel layers for broadcasting
  - Async/await support

### channels-redis==4.2.0
- **Purpose**: Redis backend for Django Channels
- **Usage**: Channel layer for production deployment
- **Note**: Optional for development (uses InMemoryChannelLayer by default)

### daphne==4.2.1
- **Purpose**: ASGI server for Django Channels
- **Usage**: Serves WebSocket connections
- **Alternative**: Can use Uvicorn in production

### asgiref==3.9.1
- **Purpose**: ASGI specification reference implementation
- **Usage**: Async support utilities
- **Required by**: Django 5.x, Channels

---

## Database

### psycopg2-binary==2.9.10
- **Purpose**: PostgreSQL database adapter
- **Usage**: Connects Django to PostgreSQL database
- **Note**: Binary distribution includes compiled C extensions
- **Alternative**: psycopg2 (requires compilation)

---

## HTTP & API Communication

### requests==2.32.3
- **Purpose**: HTTP library for Python
- **Usage**: 
  - Communication with Academic Analyzer API
  - External API calls
  - File downloads

### urllib3==2.2.1
- **Purpose**: HTTP client (dependency of requests)
- **Usage**: Connection pooling, retry logic
- **Auto-installed**: By requests

---

## AI & Question Generation

### google-generativeai==0.3.1
- **Purpose**: Google Gemini AI API client
- **Usage**: 
  - AI-powered quiz question generation
  - Content analysis from documents
  - Automatic question creation from study materials

### google-api-core==2.18.0
- **Purpose**: Core library for Google API clients
- **Required by**: google-generativeai

### google-auth==2.28.1
- **Purpose**: Google authentication library
- **Required by**: google-generativeai

### googleapis-common-protos==1.63.0
- **Purpose**: Common protocol buffer definitions
- **Required by**: google-api-core

### protobuf==4.25.3
- **Purpose**: Protocol buffer serialization
- **Required by**: Google API clients

---

## Document Processing

### PyPDF2==3.0.1
- **Purpose**: PDF file processing
- **Usage**: Extract text from PDF study materials for quiz generation
- **Features**: Read PDF content, extract text

### python-docx==1.1.0
- **Purpose**: Microsoft Word document processing
- **Usage**: Extract text from .docx files for quiz generation
- **Features**: Read Word documents, extract paragraphs

### Pillow==10.2.0
- **Purpose**: Image processing library
- **Usage**: 
  - Process images in quiz questions
  - Handle file uploads
  - Image validation
- **Features**: Image reading, format conversion, resizing

### openpyxl==3.1.2
- **Purpose**: Excel (.xlsx) file processing
- **Usage**: 
  - Bulk student enrollment via Excel files
  - Bulk marks upload
  - Download marks templates
- **Features**: Read/write Excel 2010+ files

### xlrd==2.0.1
- **Purpose**: Excel (.xls) file processing
- **Usage**: Legacy Excel file support for student data
- **Note**: Only supports .xls (pre-2007 format)

### et-xmlfile==2.0.0
- **Purpose**: XML file handling
- **Required by**: openpyxl
- **Usage**: Excel file XML structure processing

---

## Configuration & Environment

### python-dotenv==1.1.1
- **Purpose**: Environment variable management
- **Usage**: 
  - Load configuration from .env files
  - Manage API keys securely
  - Environment-specific settings
- **Files**: Reads from `.env` file

---

## WebSocket & Async Infrastructure

### autobahn==24.4.2
- **Purpose**: WebSocket protocol implementation
- **Required by**: Channels
- **Usage**: WebSocket server/client functionality

### Twisted==25.5.0
- **Purpose**: Event-driven networking engine
- **Required by**: Channels, Daphne
- **Usage**: Async I/O framework

### txaio==25.6.1
- **Purpose**: Compatibility layer for Twisted/asyncio
- **Required by**: Autobahn

### Automat==25.4.16
- **Purpose**: Finite-state machines
- **Required by**: Twisted

### hyperlink==21.0.0
- **Purpose**: Pure-Python URL parsing
- **Required by**: Twisted

### incremental==24.7.2
- **Purpose**: Versioning library
- **Required by**: Twisted

### constantly==23.10.4
- **Purpose**: Symbolic constants
- **Required by**: Twisted

### zope.interface==7.2
- **Purpose**: Interface definitions
- **Required by**: Twisted

### attrs==25.3.0
- **Purpose**: Classes without boilerplate
- **Required by**: Twisted, Automat

---

## Security & Cryptography

### cryptography==45.0.6
- **Purpose**: Cryptographic recipes and primitives
- **Usage**: 
  - Password hashing
  - Secure token generation
  - SSL/TLS support
- **Required by**: PyOpenSSL, Twisted

### pyOpenSSL==25.1.0
- **Purpose**: Python wrapper for OpenSSL
- **Usage**: SSL/TLS connections
- **Required by**: Twisted

### pyasn1==0.6.1
- **Purpose**: ASN.1 types and codecs
- **Required by**: Cryptography, Google Auth

### pyasn1-modules==0.4.2
- **Purpose**: ASN.1 protocol modules
- **Required by**: Google Auth

### service-identity==24.2.0
- **Purpose**: Service identity verification
- **Required by**: Twisted
- **Usage**: TLS certificate verification

### cffi==1.17.1
- **Purpose**: C Foreign Function Interface
- **Required by**: Cryptography

### pycparser==2.22
- **Purpose**: C parser in Python
- **Required by**: cffi

### idna==3.10
- **Purpose**: Internationalized Domain Names
- **Required by**: requests, cryptography
- **Usage**: URL encoding/decoding

---

## Code Quality & Development

### black==25.1.0
- **Purpose**: Code formatter
- **Usage**: Enforce consistent code style
- **Command**: `black .`

### isort==6.0.1
- **Purpose**: Import statement sorter
- **Usage**: Organize imports alphabetically
- **Command**: `isort .`

### mypy-extensions==1.1.0
- **Purpose**: Type checking extensions
- **Required by**: black

### pathspec==0.12.1
- **Purpose**: Path pattern matching
- **Required by**: black

### platformdirs==4.3.8
- **Purpose**: Platform-specific directories
- **Required by**: black

### click==8.2.1
- **Purpose**: Command-line interface creation
- **Required by**: black

### regex==2024.5.10
- **Purpose**: Enhanced regular expressions
- **Required by**: black

---

## Utility Packages

### colorama==0.4.6
- **Purpose**: Cross-platform colored terminal output
- **Usage**: Enhanced console logging
- **Platforms**: Windows, Linux, macOS

### tqdm==4.66.2
- **Purpose**: Progress bars
- **Usage**: Display progress for long-running operations
- **Features**: File uploads, batch processing feedback

### pytz==2024.1
- **Purpose**: Timezone definitions
- **Usage**: Timezone-aware datetime handling
- **Note**: Django 4.0+ uses zoneinfo, but pytz still used by some packages

### typing-extensions==4.14.1
- **Purpose**: Backported typing features
- **Usage**: Type hints for older Python versions
- **Required by**: Multiple packages

### six==1.16.0
- **Purpose**: Python 2/3 compatibility
- **Usage**: Cross-version compatibility utilities
- **Status**: Legacy, but required by some dependencies

### packaging==25.0
- **Purpose**: Core utilities for Python packages
- **Usage**: Version parsing, requirement handling

### sqlparse==0.5.3
- **Purpose**: SQL statement parser
- **Required by**: Django
- **Usage**: SQL formatting, syntax highlighting

### tzdata==2025.2
- **Purpose**: Timezone database
- **Required by**: Django on Windows
- **Usage**: Timezone information

---

## Installation Guide

### Quick Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate (Windows)
venv\Scripts\activate

# 2. Activate (Linux/Mac)
source venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Verify installation
pip list
```

### Selective Installation

**Minimum (Core Django)**:
```bash
pip install Django==5.2.5 djangorestframework==3.14.0 psycopg2-binary==2.9.10
```

**Add WebSocket Support**:
```bash
pip install channels==4.3.1 daphne==4.2.1
```

**Add AI Features**:
```bash
pip install google-generativeai==0.3.1
```

**Add Document Processing**:
```bash
pip install PyPDF2==3.0.1 python-docx==1.1.0 openpyxl==3.1.2 xlrd==2.0.1
```

---

## Optional Development Dependencies

Not included in requirements.txt but recommended for development:

### watchdog==3.0.0
- **Purpose**: File system event monitoring
- **Usage**: Auto-reload on file changes
- **Install**: `pip install watchdog`

### pytest==7.4.3
- **Purpose**: Testing framework
- **Usage**: Unit and integration testing
- **Install**: `pip install pytest pytest-django`

### faker==22.0.0
- **Purpose**: Fake data generation
- **Usage**: Generate test data
- **Install**: `pip install faker`

### django-debug-toolbar==4.2.0
- **Purpose**: Debug panel for Django
- **Usage**: Performance profiling, SQL query inspection
- **Install**: `pip install django-debug-toolbar`

---

## Package Conflicts & Notes

### Known Issues

1. **mypy_extensions vs mypy-extensions**
   - Both refer to the same package
   - Use: `mypy-extensions==1.1.0`

2. **typing_extensions vs typing-extensions**
   - Both refer to the same package
   - Use: `typing-extensions==4.14.1`

3. **psycopg2 vs psycopg2-binary**
   - Binary version is recommended for development
   - Production may benefit from compiled psycopg2

4. **channels-redis**
   - Optional for development
   - Required for production with multiple workers
   - Requires Redis server running

---

## Environment Variables Required

Create a `.env` file with:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DB_NAME=classroom_connect
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key-here

# Academic Analyzer API
ACADEMIC_ANALYZER_URL=http://localhost:5000
```

---

## Upgrade Instructions

### Check for Updates
```bash
pip list --outdated
```

### Upgrade Specific Package
```bash
pip install --upgrade package-name==new-version
```

### Update requirements.txt
```bash
pip freeze > requirements.txt
```

---

## Production Considerations

### Performance
- Use `channels-redis` instead of `InMemoryChannelLayer`
- Consider `psycopg2` instead of `psycopg2-binary`
- Set `DEBUG=False`

### Security
- Rotate `SECRET_KEY`
- Use environment-specific `.env` files
- Keep packages updated (security patches)

### Monitoring
- Add `django-prometheus` for metrics
- Use `sentry-sdk` for error tracking

---

## Package Size Summary

**Total size**: ~450 MB (with all dependencies)

**Breakdown**:
- Django core: ~10 MB
- Twisted: ~40 MB
- Cryptography: ~30 MB
- Google AI: ~50 MB
- Others: ~320 MB

---

## License Information

Most packages are MIT or BSD licensed. Check individual package licenses for production use:
- Django: BSD 3-Clause
- DRF: BSD 3-Clause
- Channels: BSD 3-Clause
- Google packages: Apache 2.0

---

## Support & Documentation

- **Django**: https://docs.djangoproject.com/
- **DRF**: https://www.django-rest-framework.org/
- **Channels**: https://channels.readthedocs.io/
- **Google AI**: https://ai.google.dev/docs

---

Last Updated: November 2, 2025
