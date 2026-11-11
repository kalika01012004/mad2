<template>
  <div class="container py-4 py-lg-5">
    <div class="row g-4 align-items-stretch">
      <div class="col-lg-6">
        <div class="auth-hero p-4 p-lg-5 h-100 d-flex flex-column justify-content-between shadow">
          <div>
            <span class="badge bg-info text-dark mb-3 px-3 py-2 fw-semibold">
              Examination Management Portal
            </span>
            <h1 class="fw-bold display-6 mb-3">EMP — V2</h1>
            <p class="lead opacity-90 mb-4">
              Manage course examinations, examiner slot schedules, student slot bookings, rubric evaluations, and result scorecards in one place.
            </p>
            <div class="row g-3">
              <div class="col-sm-6">
                <div class="p-3 rounded bg-white bg-opacity-10">
                  <h6 class="fw-bold mb-1"><i class="bi bi-shield-lock-fill text-warning me-2"></i>Admin</h6>
                  <small class="opacity-75">Courses, timelines, rubrics, rescheduling &amp; reports</small>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="p-3 rounded bg-white bg-opacity-10">
                  <h6 class="fw-bold mb-1"><i class="bi bi-person-workspace text-info me-2"></i>Examiner</h6>
                  <small class="opacity-75">Slot creation &amp; rubric evaluation</small>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="p-3 rounded bg-white bg-opacity-10">
                  <h6 class="fw-bold mb-1"><i class="bi bi-calendar2-check text-success me-2"></i>Student</h6>
                  <small class="opacity-75">Slot booking, CSV history export &amp; PDF scorecards</small>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="p-3 rounded bg-white bg-opacity-10">
                  <h6 class="fw-bold mb-1"><i class="bi bi-lightning-charge-fill text-danger me-2"></i>Batch Jobs</h6>
                  <small class="opacity-75">Daily reminders, monthly reports &amp; Redis cache</small>
                </div>
