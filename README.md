This is a comprehensive **README.md** that covers the entire ecosystem we’ve built for **Skilline**, including the high-end Auth pages, the Student Learning Portal, and the Instructor Management Dashboard.

---

# 🎓 Skilline: Advanced Learning Management System

**Skilline** is a premium, full-stack LMS designed to bridge the gap between instructors and students through a modern, responsive, and highly interactive interface. Built with **React** and **Tailwind CSS**, it features a robust authentication system and dedicated portals for different user roles.

## 🚀 Key Modules

### 1. 🔐 Authentication System

Custom-designed onboarding experience with a focus on security and UX.

* **Persistent Auth**: Uses `localStorage` for `accessToken` and `refreshToken`.
* **Role-Based Access**: Logic-driven routing that directs users to either the **Student** or **Instructor** dashboard upon login.
* **Modern UI**: Glassmorphic input fields, animated transitions, and real-time validation.

### 2. 📖 Student Learning Portal

A distraction-free environment for students to consume content.

* **Course Discovery**: Browse available curriculum with formatted pricing (e.g., **₦150,000**).
* **Assignment Hub**: View specific tasks per course with clear deadlines and max scores.
* **Submission Tracking**: Dynamic views to see pending and completed tasks.

### 3. 👨‍🏫 Instructor Management Dashboard

A powerful command center for educators to manage their digital classroom.

* **Course CRUD**: Create new courses or edit existing ones via sleek, slide-in modals.
* **Assignment Deployment**: One-click assignment creation with hidden `course_id` mapping.
* **Interactive Analytics**: Track student enrollment counts and tuition revenue at a glance.
* **Action Tooltips**: Custom Tailwind-based hover labels for 📝 (Assignments), 👥 (Students), and ⚙️ (Settings).

---

## 🛠️ Technical Stack

* **Frontend**: React.js (Functional Components & Hooks)
* **Styling**: Tailwind CSS (Custom `rounded-[3.5rem]`, `animate-pop-in`, and `backdrop-blur`)
* **State Management**: React `useState` / `useEffect`
* **API Client**: Axios (with Interceptors for Authorization headers)
* **Routing**: React Router DOM v6
* **Backend**: Django REST Framework (Hosted on Render)

---

## 📡 API Architecture

All requests are prefixed with `https://skilline-backend.onrender.com/api`.

### **Auth Endpoints**

* `POST /auth/login/` - Returns JWT tokens and user role.
* `POST /auth/register/` - New user account creation.

### **Instructor Endpoints**

* `GET /students/instructor/courses/` - Fetch owned courses.
* `POST /students/instructor/courses/{id}/assignments/create/` - Deploy new task.
* `PATCH /students/instructor/courses/{id}/update/` - Modify course details.

### **Student Endpoints**

* `GET /students/courses/` - View enrolled courses.
* `GET /students/courses/{id}/assignments/` - Fetch tasks for a specific course.

---

## 📂 Project Structure

```text
src/
├── components/
│   ├── Auth/
│   │   ├── Login.jsx            # Secure entry point
│   │   └── Register.jsx         # User onboarding
│   ├── Instructor/
│   │   ├── InstructorCourses.jsx # Dashboard & Modals
│   │   └── InstructorStats.jsx  # Enrollment tracking
│   ├── Student/
│   │   ├── CourseList.jsx       # Student curriculum view
│   │   └── CourseAssignments.jsx # Task viewer with courseTitle logic
├── App.jsx                      # Route & ProtectedRoute config
└── index.css                    # Skilline brand colors & animations

```

---

## 🎨 Design Principles

* **Typography**: Heavy font weights (`font-black`) for headers to establish hierarchy.
* **Colors**: Primary (`#2D3162`), Accent (`#4F46E5` Indigo), and Success (`#10B981` Emerald).
* **Feedback**: High-contrast loading states and animated "empty state" illustrations (🏜️).
* **Scannability**: Horizontal rules and card-based layouts to prevent "information fatigue."

---

## ⚙️ Development Setup

1. **Clone**: `git clone <repository-url>`
2. **Install**: `npm install`
3. **Config**: Create a `.env` file and set `REACT_APP_API_BASE=https://skilline-backend.onrender.com/api`
4. **Start**: `npm start`

---

## 🚧 Upcoming Features (Curva Roadmap)

* **Offline Mode**: Integration of USSD-based interaction for hospital selection and offline login.
* **Document Generator**: Auto-documentation feature for Curva project modules.

---

**Would you like me to add a "Troubleshooting" section specifically for the 401 Unauthorized errors we handled during the token implementation?**