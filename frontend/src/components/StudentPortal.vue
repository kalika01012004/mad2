<template>
  <div class="container-fluid px-3 px-lg-4 py-4">
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Available Examinations</div>
          <h3 class="fw-bold text-primary mb-0">{{ dash.summary.available_examinations_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Open Slots</div>
          <h3 class="fw-bold text-info mb-0">{{ dash.summary.available_slots_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Upcoming Bookings</div>
          <h3 class="fw-bold text-warning mb-0">{{ dash.summary.upcoming_examinations_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Published Results</div>
          <h3 class="fw-bold text-success mb-0">{{ dash.summary.published_results_count || 0 }}</h3>
        </div>
      </div>
    </div>

    <div class="d-flex flex-wrap justify-content-between align-items-center bg-white p-2 rounded-3 shadow-sm mb-4">
      <ul class="nav nav-pills mb-0">
        <li class="nav-item">
          <button :class="['nav-link', tab === 'dashboard' ? 'active' : '']" @click="tab = 'dashboard'">
            <i class="bi bi-house-door me-1"></i>Overview
          </button>
        </li>
        <li class="nav-item">
          <button :class="['nav-link', tab === 'browse' ? 'active' : '']" @click="tab = 'browse'">
            <i class="bi bi-search me-1"></i>Examinations &amp; Slots
          </button>
        </li>
        <li class="nav-item">
          <button :class="['nav-link', tab === 'bookings' ? 'active' : '']" @click="tab = 'bookings'">
            <i class="bi bi-calendar-check me-1"></i>My Bookings ({{ (dash.bookings || []).length }})
          </button>
        </li>
        <li class="nav-item">
          <button :class="['nav-link', tab === 'results' ? 'active' : '']" @click="tab = 'results'">
            <i class="bi bi-trophy me-1"></i>Results ({{ (dash.published_results || []).length }})
          </button>
        </li>
      </ul>

      <button class="btn btn-sm btn-outline-success fw-semibold me-2" @click="exportCsv">
        <i class="bi bi-filetype-csv me-1"></i>Export CSV History
      </button>
    </div>

    <div v-if="tab === 'dashboard'" class="row g-4">
      <div class="col-lg-6">
        <div class="card section-card p-4 h-100">
          <h5 class="fw-bold mb-3">Upcoming Examinations</h5>
          <div v-if="(dash.upcoming_examinations || []).length === 0" class="text-muted small py-3">
            No upcoming bookings. Go to "Examinations &amp; Slots" to book a slot.
          </div>
          <div v-for="b in dash.upcoming_examinations" :key="b.id" class="border rounded-3 p-3 mb-2 bg-light">
            <div class="d-flex justify-content-between">
              <span class="badge bg-dark">{{ b.course_code }}</span>
              <span class="badge bg-primary">{{ b.status }}</span>
            </div>
            <h6 class="fw-bold mt-2 mb-1">{{ b.examination_name }}</h6>
            <div class="small text-muted">
              <div><i class="bi bi-clock me-1"></i>{{ b.slot_date }} ({{ b.start_time }} - {{ b.end_time }})</div>
              <div><i class="bi bi-person-badge me-1"></i>Examiner: <strong>{{ b.examiner_name }}</strong></div>
              <div><i class="bi bi-geo-alt me-1"></i>{{ b.venue }} <a v-if="b.meeting_link" :href="b.meeting_link" target="_blank" class="ms-1">Join Link</a></div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card section-card p-4 h-100">
          <h5 class="fw-bold mb-3">Published Results</h5>
          <div v-if="(dash.published_results || []).length === 0" class="text-muted small py-3">
