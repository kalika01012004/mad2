<template>
  <div class="container-fluid px-3 px-lg-4 py-4">
    <ul class="nav nav-pills mb-4 bg-white p-2 rounded-3 shadow-sm">
      <li class="nav-item">
        <button :class="['nav-link', tab === 'dashboard' ? 'active' : '']" @click="setTab('dashboard')">
          <i class="bi bi-speedometer2 me-1"></i>Dashboard
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'courses' ? 'active' : '']" @click="setTab('courses')">
          <i class="bi bi-journal-bookmark me-1"></i>Courses ({{ courses.length }})
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'examinations' ? 'active' : '']" @click="setTab('examinations')">
          <i class="bi bi-card-checklist me-1"></i>Examinations &amp; Rubrics ({{ exams.length }})
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'examiners' ? 'active' : '']" @click="setTab('examiners')">
          <i class="bi bi-person-workspace me-1"></i>Examiners ({{ examiners.length }})
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'slots' ? 'active' : '']" @click="setTab('slots')">
          <i class="bi bi-calendar3 me-1"></i>Slots ({{ slots.length }})
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'bookings' ? 'active' : '']" @click="setTab('bookings')">
          <i class="bi bi-bookmark-check me-1"></i>Bookings ({{ bookings.length }})
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'search' ? 'active' : '']" @click="setTab('search')">
          <i class="bi bi-search me-1"></i>Search
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'jobs' ? 'active' : '']" @click="setTab('jobs')">
          <i class="bi bi-cpu me-1"></i>Batch Jobs &amp; Cache
        </button>
      </li>
    </ul>

    <div v-if="tab === 'dashboard'">
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card kpi-card p-3 bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small">Courses</div>
                <h3 class="fw-bold mb-0">{{ dash.summary.total_courses || 0 }}</h3>
              </div>
              <div class="kpi-icon bg-primary bg-opacity-10 text-primary"><i class="bi bi-book"></i></div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card kpi-card p-3 bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small">Examinations</div>
                <h3 class="fw-bold mb-0">{{ dash.summary.total_examinations || 0 }}</h3>
              </div>
              <div class="kpi-icon bg-info bg-opacity-10 text-info"><i class="bi bi-journal-check"></i></div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card kpi-card p-3 bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small">Students</div>
                <h3 class="fw-bold mb-0">{{ dash.summary.total_students || 0 }}</h3>
              </div>
              <div class="kpi-icon bg-success bg-opacity-10 text-success"><i class="bi bi-people"></i></div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card kpi-card p-3 bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small">Examiners</div>
                <h3 class="fw-bold mb-0">{{ dash.summary.total_examiners || 0 }}</h3>
              </div>
              <div class="kpi-icon bg-warning bg-opacity-10 text-warning"><i class="bi bi-person-badge"></i></div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card kpi-card p-3 bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small">Slots</div>
                <h3 class="fw-bold mb-0">{{ dash.summary.total_slots || 0 }}</h3>
              </div>
              <div class="kpi-icon bg-secondary bg-opacity-10 text-secondary"><i class="bi bi-clock-history"></i></div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card kpi-card p-3 bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small">Bookings</div>
                <h3 class="fw-bold mb-0">{{ dash.summary.total_bookings || 0 }}</h3>
              </div>
              <div class="kpi-icon bg-danger bg-opacity-10 text-danger"><i class="bi bi-calendar2-check"></i></div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-6">
          <div class="card section-card p-3">
            <h6 class="fw-bold mb-3"><i class="bi bi-bar-chart-fill text-primary me-2"></i>Bookings &amp; Evaluations by Examination</h6>
            <div class="chart-box">
              <canvas ref="chartPopularExams"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card section-card p-3">
            <h6 class="fw-bold mb-3"><i class="bi bi-person-lines-fill text-success me-2"></i>Examiner Workload</h6>
            <div class="chart-box">
              <canvas ref="chartExaminerWorkload"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card section-card p-3">
            <h6 class="fw-bold mb-3"><i class="bi bi-pie-chart-fill text-info me-2"></i>Booking Status</h6>
            <div class="chart-box">
              <canvas ref="chartBookingTrends"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card section-card p-3">
            <h6 class="fw-bold mb-3"><i class="bi bi-diagram-3-fill text-warning me-2"></i>Examination Status</h6>
            <div class="chart-box">
