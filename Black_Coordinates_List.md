# Black Coordinates List

## 1. Operational Background

In recent years, persistent hostile cyber activity has been conducted against government entities, sensitive infrastructure (such as the light rail in the Dan region), and individuals of importance. This activity is carried out through decentralized infrastructure, use of rotating IP addresses, and concealment of operational sources behind various technological layers.

The scope of activity, frequency, and potential damage have led to the understanding that dealing with the threat cannot remain solely at the digital level. A deeper connection is required between technological information and the physical reality behind it.

The organization has made the decision to develop an infrastructural capability that will enable a broader view of the arena — one that will serve as a basis for intelligence, investigative, and operational activities going forward.

At this stage, after the operational need has been defined and its importance clarified, **you are called to the mission**.

You are required to establish the **Black Coordinates List** — an infrastructural system that will be built accurately, stably, and in a scalable manner, and will serve as a core component in a larger array of systems and capabilities.

The emphasis in this project is not on sophistication or algorithms, but on **proper infrastructure construction**: understanding information flow, separation of responsibilities, and the ability to rely on the system as a basis for continued operations.

## 2. What the System Does

The Black Coordinates List system is an infrastructural system whose purpose is to perform the following operations:

1. **Receive IP addresses** related to cyber activity
2. **Convert IP addresses to geographic coordinates** using an external service
3. **Transfer coordinates** between internal services in the system
4. **Store coordinates** in a fast Key-Value based database
5. **Centralized retrieval** of all coordinates saved in the system

The system operates as a **core infrastructure layer** and provides data for future use by other systems, services, or entities in the organization.

## 3. General System Architecture

The Black Coordinates List system is built as an infrastructural system based on Services, where each component is responsible for a defined and clear domain. The system uses HTTP communication between services, an external service for converting IP to geographic location, and a fast Key-Value type database for storage and retrieval.

### Core Technologies in the System:

- **Python + FastAPI** for Backend services
- **HTTP (REST)** for communication between components
- **External service** for converting IP to coordinates
- **Redis** as a fast infrastructural database
- **Container-based environment**

The architecture is designed so that each component can be understood, tested, and replaced without affecting the rest of the system.

### System Components

The system consists of three main components:

1. **IP Reception and Location Conversion Service (Service A)**
2. **Coordinate Storage and Retrieval Service (Service B)**
3. **Redis Database**

Below is a detailed breakdown of responsibilities for each component.

### 3.1 Service A – IP Resolution Service

#### Role in the System
This service serves as the entry point for external information. It is responsible for receiving IP addresses, converting them to geographic locations, and transferring the data forward to an internal service.

#### What the Service Does:
- Exposes API for receiving IP addresses
- Sends request to external service for IP to location conversion
- Receives and processes the external service's response (coordinates)
- Sends coordinates to the storage service (Service B, detailed below)

#### What the Service Does NOT Do:
- Does not store data
- Does not work directly with Redis
- Does not perform data retrievals
- Does not make decisions or analyze data
- Is not responsible for displaying information

This is an **Adapter service** between the external world and the internal system.

### 3.2 Service B – Coordinates Storage Service

#### Role in the System
This service serves as the storage and retrieval layer of the system. It is responsible for receiving coordinates, storing them in an organized manner, and returning them on demand.

#### What the Service Does:
- Exposes internal API for receiving coordinates (from Service A)
- Performs basic validation of incoming data using Pydantic
- Saves data in Redis
- Enables centralized retrieval of all saved data

#### What the Service Does NOT Do:
- Does not contact external services
- Does not know the data source (from which server, user, or system)
- Does not perform calculations or analysis

This is a "quiet" infrastructural service whose purpose is one: **reliable storage and retrieval**.

### 3.3 Redis – The Database

#### Role in the System
Redis serves as a fast database for storing coordinates.

#### Key Characteristics:
- Key-Value based
- In-Memory with basic Persistency
- Fast and simple access
- Suitable for storing simple data structures

#### Usage in the Project:
- Storing coordinates as simple data structures
- General retrieval of all values
- No dynamic TTL usage
- No business logic within the database

### Guiding Architectural Principle

Each component in the system:
- Knows only the minimum required
- Is not dependent on the internal logic of other components

This structure enables:
- **Simplicity**
- **Testability**
- **Easy maintenance**
- **Future expansion without breaking the system**

## 4. Complete System Information Flow

### Primary Flow: IP Reception and Coordinate Storage

1. An external entity (agent, system, or testing tool) sends a POST request to Service A with an IP address
2. Service A receives the request and begins processing the IP address
3. Service A sends an HTTP request to an external service for IP to geographic location conversion
4. The external service returns to Service A data including geographic coordinates
5. Service A performs basic processing of the data received from the external service and extracts only relevant information
6. After receiving valid data, Service A sends an internal POST request to Service B with the coordinates
7. Service B receives the request and performs basic validation of the data
8. Service B stores the coordinates in the Redis database
9. The process ends after the data is successfully saved in the database

### Secondary Flow: Data Retrieval

1. An internal entity (testing tool, future system, or additional service) sends a GET request to Service B
2. Service B receives the request and performs retrieval of all coordinates from the database
3. Redis returns the saved data
4. Service B returns the list of coordinates, corresponding to the relevant IP address, to the requesting entity

### Important Emphasis on Information Flow

- Each flow starts with an explicit HTTP request
- Service A does not store data and does not access Redis
- Service B does not contact external services and does not know the data source

## 6. Work Division and Responsibility Between Developers

The Black Coordinates List system is developed by a small team, with responsibility clearly divided between two developers. The division is designed to enable parallel work, clear responsibility, and minimize dependency between components.

Each developer is responsible for one service, including its development, testing, and integration with the rest of the system.

### Developer A – Service A (IP Resolution Service)

#### Area of Responsibility
Developer A is responsible for everything related to IP address reception and communication with the external world.

#### Main Responsibilities:
- Develop Service A using FastAPI
- Define Endpoint for IP address reception
- Implement call to external service for IP to geographic location conversion
- Basic processing of received data
- Send coordinates to Service B via internal HTTP request
- Handle communication errors and data errors
- Manual end-to-end flow testing until data transmission

#### Responsibility Boundaries:
- Does not store data
- Does not work directly with Redis
- Does not perform retrievals
- Is not responsible for storage structure

### Developer B – Service B (Coordinates Storage Service)

#### Area of Responsibility
Developer B is responsible for the storage and retrieval layer of the system.

#### Main Responsibilities:
- Develop Service B using FastAPI
- Define Endpoint for receiving coordinates from Service A
- Basic validation of incoming data
- Connect to Redis using environment variables
- Store coordinates in agreed data structure
- Implement Endpoint for centralized retrieval of all data
- Test storage, retrieval, and Redis behavior

#### Responsibility Boundaries:
- Does not contact external services
- Does not know the data source (IP, user, system)
- Does not perform calculations or analysis
- Is not responsible for data flow before storage

### Shared Responsibility

Both developers are jointly responsible for:
- Coordinating data structure passed between services
- Defining clear contract between Service A and Service B
- Integration testing between services
- Maintaining clear, readable, and maintainable code

This work division simulates work in a real Backend team, where each developer is responsible for a defined component but understands the overall system flow.

## 7. Git Work Standard and Branching Strategy

### General Repository Structure

- One repository for the entire system
- Each service in a separate folder
- README file briefly explaining the project structure

### Branching Strategy

Work is performed using a clear Branching strategy:

#### `main`
- Contains only stable code (that actually works after testing)
- No direct work on this branch

#### `dev`
- Main development branch
- All changes merge here after approval

#### `feature/*`
- Work branches for specific tasks
- Each task developed in a separate branch

#### Example Branch Names:
- `feature/service-a-ip-resolution`
- `feature/service-b-storage`
- `feature/redis-connection`

### Work Process

1. Create new Branch from `dev`
2. Work only on it
3. Make small and clear Commits
4. Open Pull Request to `dev`
5. After approval — perform Merge
6. **Do not perform direct Merge without Pull Request** (which includes review by the second team member, as detailed below)

### Pull Requests and Code Review (Mandatory)

**Every Pull Request must undergo Code Review by another developer on the team.**

- No self-approval
- Each developer performs Review of the other developer's code
- Only after Review and explicit approval can Merge be performed
- Code that has not undergone Code Review — does not enter the system

### Commit Message Writing Convention

Every Commit describes one clear change.

#### Recommended Structure:
```
<type>: <short description>
```

#### Common Commit Types:
- `feat`: Adding functionality
- `fix`: Bug fix
- `refactor`: Structural change without behavior change
- `docs`: Documentation
- `chore`: Maintenance or configuration

#### Examples:
- `feat: add IP resolution endpoint`
- `fix: handle invalid IP input`
- `refactor: separate service logic from route`
- `docs: update README`

### Important Emphasis

- One Commit = one change
- Don't push broken code
- Don't mix multiple topics in the same Commit
- Each developer is responsible for the quality of code they introduce

Working according to this standard is an integral part of the mission and simulates a real work process in professional development teams.

## 8. Folder and File Structure

The project structure is divided by services, where each service is isolated and clear, containing only the files required for its responsibility.

The structure is designed to:
- Enable parallel work between developers
- Maintain separation of responsibilities
- Be clear even to someone reading the project for the first time

### General Project Structure

```
black-coordinates-list/
│
├── service-a/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── services.py
│   │   ├── Dockerfile
│   │   └── schemas.py
│   │
│   ├── requirements.txt
│   └── README.md
│
├── service-b/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── storage.py
│   │   ├── Dockerfile
│   │   └── schemas.py
│   │
│   ├── requirements.txt
│   └── README.md
│
├── k8s/
│   ├── service-a-deployment.yaml
│   ├── service-a-service.yaml
│   ├── service-b-deployment.yaml
│   ├── service-b-service.yaml
│   ├── redis-deployment.yaml
│   └── redis-service.yaml
│
├── docker-compose.yml
├── .env.example
└── README.md
```

### Structure Explanation – Professional Team Level

#### Root Directory

**`black-coordinates-list/`** — Contains all system components

**`docker-compose.yml`** — Enables local execution of all services and Redis

**`.env.example`** — Example of environment variables (does not contain secrets)

**`README.md`** — General description of the project, architecture, and execution method

**`k8s/`** — Contains all Kubernetes YAML configuration files for deployment:
- Deployment files for each service
- Service files for internal and external communication
- Redis deployment and service configuration

### Service A – IP Resolution Service

```
service-a/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── services.py
│   ├── Dockerfile
│   └── schemas.py
```

#### Responsibility Division:

**`main.py`** — Creating FastAPI application and connecting routes

**`routes.py`** — Endpoints only. No complex logic.

**`services.py`** — Work logic:
- Call to external service
- Data processing
- Sending to Service B

**`schemas.py`** — Request and response models (Pydantic)

### Service B – Coordinates Storage Service

```
service-b/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── storage.py
│   ├── Dockerfile
│   └── schemas.py
```

#### Responsibility Division:

**`main.py`** — Creating FastAPI application and connecting routes

**`routes.py`** — Endpoints:
- Receiving coordinates
- Data retrieval

**`storage.py`** — Working with Redis:
- Connection
- Storage
- Retrieval

**`schemas.py`** — Data models (Pydantic)

### Important Guidelines

- No logic code in `routes.py`
- Each file is responsible for one clear task
- No direct dependency between Service A and Redis
- Communication between services is only through HTTP

## 9. Deployment Requirements – Kubernetes (Minikube)

The Black Coordinates List system must be deployed on Kubernetes in a local Minikube environment.

### General Deployment Requirements:

1. All system components will run as Pods within Kubernetes
2. Each Backend service will be defined so it can be restarted without dependency on a specific instance
3. The storage component will be defined so that its data is not dependent on a one-time execution
4. Communication between system components will be performed only through Kubernetes Services
5. At least one service will be accessible from the local computer for testing purposes
6. **No use of port-forward**
7. Deployment will be performed using YAML files only and managed through the terminal

### Optional Extension

Students interested in doing so will be able, later on, to deploy the same system also in a managed Kubernetes environment (such as OpenShift), while using the same principles and similar YAML files.
