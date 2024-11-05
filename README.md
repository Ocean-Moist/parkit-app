# parkit! 🚗

A backend only (for now) modern social media platform that gamifies parking by rating parking jobs using computer vision and machine learning. Users can post pictures of parked cars, and our system automatically detects vehicles, recognizes license plates, and calculates a parking score based on alignment within parking spaces.

## 🌟 Features

- **Intelligent Parking Analysis**
   - Vehicle detection using YOLOv8
   - License plate recognition with FastANPR
   - Automated parking score calculation based on alignment
   - Vehicle color and model recognition

- **Social Platform**
   - User profiles and authentication via Google OAuth2
   - Photo sharing and scoring system
   - Community engagement through parking ratings
   - User statistics and leaderboards

- **Secure(ish) Backend**
   - RESTful API built with FastAPI
   - PostgreSQL database for data persistence
   - JWT-based authentication
   - Kubernetes-ready deployment configuration

## 🔧 Technical Architecture

### Backend Stack
- **Web Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: Google OAuth2
- **ML/CV Components**:
   - YOLOv8 for vehicle detection
   - FastANPR for license plate recognition
   - TensorFlow for vehicle color/model classification
- **Deployment**: Kubernetes

### Directory Structure
```
backend/
├── app/
│   ├── auth.py           # Authentication logic
│   ├── database.py       # Database models and configuration
│   ├── main.py          # FastAPI application and routes
│   ├── parking_rating.py # Parking score calculation
│   ├── posts.py         # Post handling logic
│   └── utils.py         # Utility functions
├── k8s/                 # Kubernetes configuration files
└── Dockerfile          # Container configuration
```

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- PostgreSQL
- Kubernetes cluster (for deployment)
- Google OAuth2 credentials

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/parkit.git
cd parkit
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/app/requirements.txt
```

4. Set up environment variables:
```bash
export GOOGLE_CLIENT_ID="your_client_id"
export GOOGLE_CLIENT_SECRET="your_client_secret"
export GOOGLE_REDIRECT_URI="your_redirect_uri"
```

5. Start the development server:
```bash
cd backend/app
uvicorn main:app --reload
```

### Kubernetes Deployment

1. Create the namespace:
```bash
kubectl apply -f backend/k8s/ns.yml
```

2. Deploy PostgreSQL:
```bash
kubectl apply -f backend/k8s/postgres-configmap.yml
kubectl apply -f backend/k8s/postgres-deployment.yml
kubectl apply -f backend/k8s/postgres-service.yml
```

3. Deploy the application:
```bash
kubectl apply -f backend/k8s/deployment.yml
kubectl apply -f backend/k8s/parkit-service.yml
```

The MAKEFILE is specific to OpenRC and minikube.

## 📈 Development Roadmap

### In Progress
- [ ] Fix current bugs and tidy app tech debt.
- [ ] Improved error handling and input validation
- [ ] User profile customization
- [ ] Enhanced parking score algorithm
- [ ] API documentation with Swagger/OpenAPI

### Planned Features
- [ ] Swift frontend 

## 🐛 Known Issues

1. **Security Concerns**
   - JWT secret key configuration needs improvement
   - Sensitive information should be moved to environment variables

2. **Technical Debt**
   - Need better error handling
   - Lack of comprehensive test coverage
   - `vehicle_detection_tracker` integration needs refinement

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [vehicle_detection_tracker](https://github.com/sergio11/vehicle_detection_tracker) for vehicle detection capabilities
- YOLOv8 team for the object detection model
- FastAPI team for the excellent web framework
- The open source community for various tools and libraries used in this project
