<template>
  <div class="container-fluid px-3 px-lg-4 py-4">
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Assigned Examinations</div>
          <h3 class="fw-bold text-primary mb-0">{{ dash.summary.assigned_examinations_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Created Slots</div>
          <h3 class="fw-bold text-info mb-0">{{ dash.summary.created_slots_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Booked Students</div>
          <h3 class="fw-bold text-success mb-0">{{ dash.summary.booked_students_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Pending Evaluations</div>
          <h3 class="fw-bold text-warning mb-0">{{ dash.summary.pending_evaluations_count || 0 }}</h3>
        </div>
      </div>
    </div>

    <ul class="nav nav-pills mb-4 bg-white p-2 rounded-3 shadow-sm">
      <li class="nav-item">
        <button :class="['nav-link', tab === 'dashboard' ? 'active' : '']" @click="tab = 'dashboard'">
          <i class="bi bi-easel me-1"></i>Assigned Examinations
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'slots' ? 'active' : '']" @click="tab = 'slots'">
          <i class="bi bi-calendar-plus me-1"></i>My Slots ({{ (dash.slots || []).length }})
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'evaluations' ? 'active' : '']" @click="tab = 'evaluations'">
          <i class="bi bi-clipboard2-check me-1"></i>Booked Students &amp; Evaluations ({{ (dash.bookings || []).length }})
        </button>
      </li>
    </ul>

    <div v-if="tab === 'dashboard'" class="card section-card p-4">
      <h5 class="fw-bold mb-3">Assigned Examinations</h5>
      <div class="row g-3">
        <div v-for="ex in dash.assigned_examinations" :key="ex.id" class="col-md-6">
          <div class="border rounded-3 p-3 h-100 bg-white">
            <div class="d-flex justify-content-between mb-2">
              <span class="badge bg-dark">{{ ex.course_code }} - {{ ex.course_name }}</span>
              <span class="badge bg-primary">{{ ex.status }}</span>
            </div>
            <h5 class="fw-bold mb-1">{{ ex.name }}</h5>
            <p class="small text-muted mb-2">
              Type: <strong>{{ ex.exam_type }}</strong> | Duration: <strong>{{ ex.duration }} mins</strong> | Max Marks: <strong>{{ ex.max_marks }}</strong>
            </p>
            <div class="small bg-light p-2 rounded mb-3">
              <div><strong>Slot Creation:</strong> {{ ex.slot_creation_start }} to {{ ex.slot_creation_end }}</div>
              <div><strong>Student Booking:</strong> {{ ex.slot_booking_start }} to {{ ex.slot_booking_end }}</div>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <span :class="['badge', ex.can_create_slots ? 'bg-success' : 'bg-secondary']">
                {{ ex.can_create_slots ? 'Slot Creation Open' : 'Slot Creation Closed' }}
              </span>
              <button
                v-if="ex.can_create_slots"
                class="btn btn-sm btn-primary"
                @click="slotForm.examination_id = ex.id; tab = 'slots'"
              >
                Create Slots
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
