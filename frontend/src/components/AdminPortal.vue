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
              <canvas ref="chartExamStatus"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'courses'" class="row g-4">
      <div class="col-lg-4">
        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">
            {{ editingCourse ? 'Edit Course' : 'Add Course' }}
          </h5>
          <form @submit.prevent="saveCourse">
            <div class="mb-3">
              <label class="form-label small fw-medium">Course Code <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model.trim="courseForm.code" required placeholder="CS2002" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Course Name <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model.trim="courseForm.name" required placeholder="Modern Application Development II" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col-7">
                <label class="form-label small fw-medium">Department</label>
                <input type="text" class="form-control" v-model.trim="courseForm.department" required />
              </div>
              <div class="col-5">
                <label class="form-label small fw-medium">Credits</label>
                <input type="number" class="form-control" v-model.number="courseForm.credits" min="1" max="10" required />
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-7">
                <label class="form-label small fw-medium">Semester</label>
                <input type="text" class="form-control" v-model.trim="courseForm.semester" />
              </div>
              <div class="col-5">
                <label class="form-label small fw-medium">Status</label>
                <select class="form-select" v-model="courseForm.status">
                  <option>Active</option>
                  <option>Inactive</option>
                  <option>Archived</option>
                </select>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Description</label>
              <textarea class="form-control" rows="3" v-model.trim="courseForm.description"></textarea>
            </div>
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary flex-grow-1">
                {{ editingCourse ? 'Update' : 'Create' }}
              </button>
              <button v-if="editingCourse" type="button" class="btn btn-outline-secondary" @click="resetCourseForm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">Courses ({{ courses.length }})</h5>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Credits</th>
                  <th>Exams</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in courses" :key="c.id">
                  <td><span class="badge bg-dark">{{ c.code }}</span></td>
                  <td>
                    <div class="fw-semibold">{{ c.name }}</div>
                    <small class="text-muted">{{ c.description }}</small>
                  </td>
                  <td>{{ c.department }}</td>
                  <td>{{ c.credits }}</td>
                  <td><span class="badge bg-info text-dark">{{ c.examinations_count }}</span></td>
                  <td>
                    <span :class="['badge', c.status === 'Active' ? 'bg-success' : 'bg-secondary']">{{ c.status }}</span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="editCourse(c)"><i class="bi bi-pencil"></i></button>
                      <button class="btn btn-outline-danger" @click="removeCourse(c)"><i class="bi bi-trash"></i></button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'examinations'" class="row g-4">
      <div class="col-lg-4">
        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">{{ editingExam ? 'Edit Examination' : 'New Examination' }}</h5>
          <form @submit.prevent="saveExam">
            <div class="mb-2">
              <label class="form-label small fw-medium">Course <span class="text-danger">*</span></label>
              <select class="form-select" v-model="examForm.course_id" required>
                <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.code }} - {{ c.name }}</option>
              </select>
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Examination Name <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model.trim="examForm.name" required placeholder="End-Term Viva" />
            </div>
            <div class="row g-2 mb-2">
              <div class="col-6">
                <label class="form-label small fw-medium">Type</label>
                <select class="form-select" v-model="examForm.exam_type">
                  <option>Viva</option>
                  <option>Practical</option>
                  <option>Project Demo</option>
                  <option>Assessment</option>
                </select>
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Duration (mins)</label>
                <input type="number" class="form-control" v-model.number="examForm.duration" min="5" required />
              </div>
            </div>
            <div class="row g-2 mb-2">
              <div class="col-6">
                <label class="form-label small fw-medium">Max Marks</label>
                <input type="number" class="form-control" v-model.number="examForm.max_marks" min="1" required />
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Passing Marks</label>
                <input type="number" class="form-control" v-model.number="examForm.passing_marks" min="0" required />
              </div>
            </div>
            <div class="row g-2 mb-2">
              <div class="col-6">
                <label class="form-label small fw-medium">Slot Creation Start</label>
                <input type="date" class="form-control" v-model="examForm.slot_creation_start" required />
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Slot Creation End</label>
                <input type="date" class="form-control" v-model="examForm.slot_creation_end" required />
              </div>
            </div>
            <div class="row g-2 mb-2">
              <div class="col-6">
                <label class="form-label small fw-medium">Booking Start</label>
                <input type="date" class="form-control" v-model="examForm.slot_booking_start" required />
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Booking End</label>
                <input type="date" class="form-control" v-model="examForm.slot_booking_end" required />
              </div>
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Status</label>
              <select class="form-select" v-model="examForm.status">
                <option>Draft</option>
                <option>Slot Creation</option>
                <option>Booking Open</option>
                <option>Closed</option>
                <option>Completed</option>
              </select>
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Assigned Examiners</label>
              <select class="form-select" multiple v-model="examForm.examiner_ids" style="height: 85px;">
                <option v-for="exm in examiners" :key="exm.id" :value="exm.id">
                  {{ exm.name }} ({{ exm.department }})
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Instructions</label>
              <textarea class="form-control" rows="2" v-model.trim="examForm.instructions"></textarea>
            </div>
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary flex-grow-1">
                {{ editingExam ? 'Save' : 'Create' }}
              </button>
              <button v-if="editingExam" type="button" class="btn btn-outline-secondary" @click="resetExamForm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="col-lg-8">
        <div v-if="activeRubricExam" class="card section-card p-4 mb-4 border-start border-4 border-primary">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h5 class="fw-bold mb-0 text-primary">
                Rubrics — {{ activeRubricExam.name }}
              </h5>
              <small class="text-muted">Max Marks: {{ activeRubricExam.max_marks }}</small>
            </div>
            <button class="btn btn-sm btn-outline-secondary" @click="activeRubricExam = null">Close</button>
          </div>

          <form class="row g-2 mb-3 align-items-end" @submit.prevent="addRubric">
            <div class="col-md-4">
              <label class="form-label small">Criterion *</label>
              <input type="text" class="form-control form-control-sm" v-model.trim="rubricForm.criterion_name" required placeholder="Code Quality" />
            </div>
            <div class="col-md-2">
              <label class="form-label small">Max Marks *</label>
              <input type="number" class="form-control form-control-sm" v-model.number="rubricForm.max_marks" min="1" required />
            </div>
            <div class="col-md-2">
              <label class="form-label small">Weightage %</label>
              <input type="number" class="form-control form-control-sm" v-model.number="rubricForm.weightage" min="1" max="100" required />
            </div>
            <div class="col-md-3">
              <label class="form-label small">Description</label>
              <input type="text" class="form-control form-control-sm" v-model.trim="rubricForm.description" />
            </div>
            <div class="col-md-1">
              <button type="submit" class="btn btn-sm btn-success w-100"><i class="bi bi-plus-lg"></i></button>
            </div>
          </form>

          <div class="table-responsive">
            <table class="table table-sm table-bordered mb-0">
              <thead class="table-light">
                <tr>
                  <th>Criterion</th>
                  <th>Max Marks</th>
                  <th>Weightage</th>
                  <th>Description</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in rubrics" :key="r.id">
                  <td class="fw-semibold">{{ r.criterion_name }}</td>
                  <td>{{ r.max_marks }}</td>
                  <td>{{ r.weightage }}%</td>
                  <td class="small text-muted">{{ r.description }}</td>
                  <td>
                    <button class="btn btn-xs btn-outline-danger btn-sm py-0" @click="removeRubric(r)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="rubrics.length === 0">
                  <td colspan="5" class="text-center text-muted small">No rubrics added yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">Examinations</h5>
          <div v-for="ex in exams" :key="ex.id" class="border rounded-3 p-3 mb-3 bg-white shadow-sm">
            <div class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-2">
              <div>
                <span class="badge bg-dark me-2">{{ ex.course_code }}</span>
                <span class="badge bg-info text-dark me-2">{{ ex.exam_type }}</span>
                <span class="badge bg-primary">{{ ex.status }}</span>
                <h6 class="fw-bold mt-2 mb-1">{{ ex.name }}</h6>
                <div class="small text-muted">
                  Duration: <strong>{{ ex.duration }} mins</strong> | Max Marks: <strong>{{ ex.max_marks }}</strong> |
                  Slots: <strong>{{ ex.slots_count }}</strong> ({{ ex.available_slots_count }} open) |
                  Rubrics: <strong>{{ (ex.rubrics || []).length }}</strong>
                </div>
              </div>
              <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary" @click="openRubrics(ex)">
                  Rubrics ({{ (ex.rubrics || []).length }})
                </button>
                <button class="btn btn-outline-secondary" @click="editExam(ex)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger" @click="removeExam(ex)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>

            <div class="row g-2 small bg-light p-2 rounded mb-2">
              <div class="col-md-4">
                <strong>Slot Creation:</strong><br />
                {{ ex.slot_creation_start }} to {{ ex.slot_creation_end }}
              </div>
              <div class="col-md-4">
                <strong>Slot Booking:</strong><br />
                {{ ex.slot_booking_start }} to {{ ex.slot_booking_end }}
              </div>
              <div class="col-md-4">
                <strong>Examiners:</strong><br />
                <span v-if="ex.assigned_examiners && ex.assigned_examiners.length">
                  {{ ex.assigned_examiners.map(a => a.name).join(', ') }}
                </span>
                <span v-else class="text-danger">None</span>
              </div>
            </div>

            <div class="d-flex flex-wrap gap-2 mt-2">
              <button
                :class="['btn', 'btn-sm', ex.slot_creation_open ? 'btn-warning' : 'btn-outline-warning text-dark']"
                @click="flipSlotCreation(ex)"
              >
                {{ ex.slot_creation_open ? 'Close Slot Creation' : 'Open Slot Creation' }}
              </button>

              <button
                :class="['btn', 'btn-sm', ex.slot_booking_open ? 'btn-primary' : 'btn-outline-primary']"
                @click="flipSlotBooking(ex)"
              >
                {{ ex.slot_booking_open ? 'Close Slot Booking' : 'Open Slot Booking' }}
              </button>

              <button
                :class="['btn', 'btn-sm', ex.results_published ? 'btn-success' : 'btn-outline-success']"
                @click="flipResults(ex)"
              >
                {{ ex.results_published ? 'Unpublish Results' : 'Publish Results' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'examiners'" class="row g-4">
      <div class="col-lg-4">
        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">{{ editingExaminer ? 'Edit Examiner' : 'Add Examiner' }}</h5>
          <form @submit.prevent="saveExaminer">
            <div class="mb-2">
              <label class="form-label small fw-medium">Full Name <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model.trim="examinerForm.name" required placeholder="Dr. Vikram Patel" />
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Email <span class="text-danger">*</span></label>
              <input type="email" class="form-control" v-model.trim="examinerForm.email" :disabled="!!editingExaminer" required placeholder="vikram@emp.edu" />
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">
                {{ editingExaminer ? 'New Password (optional)' : 'Password *' }}
              </label>
              <input type="text" class="form-control" v-model="examinerForm.password" :required="!editingExaminer" />
            </div>
            <div class="row g-2 mb-2">
              <div class="col-6">
                <label class="form-label small fw-medium">Department</label>
                <input type="text" class="form-control" v-model.trim="examinerForm.department" required />
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Designation</label>
                <input type="text" class="form-control" v-model.trim="examinerForm.designation" />
              </div>
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Contact</label>
              <input type="text" class="form-control" v-model.trim="examinerForm.contact_details" />
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Specialization</label>
              <input type="text" class="form-control" v-model.trim="examinerForm.specialization" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Status</label>
              <select class="form-select" v-model="examinerForm.status">
                <option>Active</option>
                <option>Inactive</option>
              </select>
            </div>
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary flex-grow-1">
                {{ editingExaminer ? 'Update' : 'Add Examiner' }}
              </button>
              <button v-if="editingExaminer" type="button" class="btn btn-outline-secondary" @click="resetExaminerForm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">Examiners ({{ examiners.length }})</h5>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Contact</th>
                  <th>Exams</th>
                  <th>Slots / Evals</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="exm in examiners" :key="exm.id">
                  <td>
                    <div class="fw-bold">{{ exm.name }}</div>
                    <small class="text-muted">{{ exm.email }}</small>
                  </td>
                  <td>
                    <div>{{ exm.department }}</div>
                    <small class="text-muted">{{ exm.designation }} — {{ exm.specialization }}</small>
                  </td>
                  <td class="small">{{ exm.contact_details || 'N/A' }}</td>
                  <td><span class="badge bg-primary">{{ exm.assigned_exams_count }}</span></td>
                  <td>
                    <span class="badge bg-info text-dark me-1">{{ exm.slots_count }} slots</span>
                    <span class="badge bg-success">{{ exm.evaluations_count }} evals</span>
                  </td>
                  <td>
                    <span :class="['badge', exm.status === 'Active' ? 'bg-success' : 'bg-danger']">{{ exm.status }}</span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="editExaminer(exm)"><i class="bi bi-pencil"></i></button>
                      <button class="btn btn-outline-danger" @click="removeExaminer(exm)"><i class="bi bi-trash"></i></button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'slots'">
      <div v-if="slotToEdit" class="card section-card p-4 mb-4 border-start border-4 border-warning">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-bold mb-0">
            Reschedule / Reassign Slot #{{ slotToEdit.id }}
          </h5>
          <button class="btn-close" @click="slotToEdit = null"></button>
        </div>
        <form class="row g-3" @submit.prevent="saveSlotReschedule">
          <div class="col-md-3">
            <label class="form-label small fw-medium">Date</label>
            <input type="date" class="form-control" v-model="slotEditForm.date" required />
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-medium">Start Time</label>
            <input type="time" class="form-control" v-model="slotEditForm.start_time" required />
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-medium">End Time</label>
            <input type="time" class="form-control" v-model="slotEditForm.end_time" required />
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-medium">Examiner</label>
            <select class="form-select" v-model="slotEditForm.examiner_id" required>
              <option v-for="exm in examiners" :key="exm.id" :value="exm.id">
                {{ exm.name }} ({{ exm.department }})
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-medium">Max Capacity</label>
            <input type="number" class="form-control" v-model.number="slotEditForm.max_capacity" min="1" required />
          </div>
          <div class="col-md-4">
            <label class="form-label small fw-medium">Meeting Link</label>
            <input type="text" class="form-control" v-model="slotEditForm.meeting_link" />
          </div>
          <div class="col-md-5">
            <label class="form-label small fw-medium">Reason</label>
            <input type="text" class="form-control" v-model="slotEditForm.reason" required />
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button type="submit" class="btn btn-warning fw-semibold w-100">Update Slot</button>
          </div>
        </form>
      </div>

      <div class="card section-card p-4">
        <h5 class="fw-bold mb-3">All Examination Slots ({{ slots.length }})</h5>
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Examination</th>
                <th>Examiner</th>
                <th>Date &amp; Time</th>
                <th>Seats</th>
                <th>Venue</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in slots" :key="s.id">
                <td>#{{ s.id }}</td>
                <td>
                  <span class="badge bg-dark me-1">{{ s.course_code }}</span>
                  <strong>{{ s.examination_name }}</strong>
                </td>
                <td>
                  <div class="fw-semibold">{{ s.examiner_name }}</div>
                  <small class="text-muted">{{ s.examiner_department }}</small>
                </td>
                <td>
                  <div>{{ s.date }}</div>
                  <small class="text-muted">{{ s.start_time }} - {{ s.end_time }}</small>
                </td>
                <td>
                  <span class="fw-bold">{{ s.available_seats }}</span> / {{ s.max_capacity }}
                  <small class="text-muted ms-1">({{ s.booked_count }} booked)</small>
                </td>
                <td class="small">
                  <div>{{ s.venue }}</div>
                  <a v-if="s.meeting_link" :href="s.meeting_link" target="_blank" class="small">Meeting Link</a>
                </td>
                <td>
                  <span
                    :class="[
                      'badge',
                      s.status === 'Available' ? 'bg-success' : s.status === 'Full' ? 'bg-warning text-dark' : 'bg-secondary',
                    ]"
                  >
                    {{ s.status }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-warning text-dark" @click="startSlotReschedule(s)">
                    Reschedule / Reassign
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="tab === 'bookings'">
      <div v-if="bookingToMove" class="card section-card p-4 mb-4 border-start border-4 border-primary">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-bold mb-0">
            Reschedule Booking #{{ bookingToMove.id }} — {{ bookingToMove.student_name }}
          </h5>
          <button class="btn-close" @click="bookingToMove = null"></button>
        </div>
        <form class="row g-3 align-items-end" @submit.prevent="saveBookingReschedule">
          <div class="col-md-5">
            <label class="form-label small fw-medium">Target Slot</label>
            <select class="form-select" v-model="bookingMoveForm.new_slot_id" required>
              <option v-for="s in getExamSlots(bookingToMove.examination_id)" :key="s.id" :value="s.id">
                Slot #{{ s.id }} | {{ s.date }} ({{ s.start_time }}-{{ s.end_time }}) | {{ s.examiner_name }} | Avail: {{ s.available_seats }}
              </option>
            </select>
          </div>
          <div class="col-md-5">
            <label class="form-label small fw-medium">Reason</label>
            <input type="text" class="form-control" v-model="bookingMoveForm.reason" required />
          </div>
          <div class="col-md-2">
            <button type="submit" class="btn btn-primary w-100">Save</button>
          </div>
        </form>
      </div>

      <div class="card section-card p-4">
        <h5 class="fw-bold mb-3">Student Bookings ({{ bookings.length }})</h5>
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Student</th>
                <th>Examination</th>
                <th>Date &amp; Time</th>
                <th>Examiner</th>
                <th>Status</th>
                <th>Evaluation</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td>#{{ b.id }}</td>
                <td>
                  <div class="fw-bold">{{ b.student_name }}</div>
                  <small class="text-muted">{{ b.student_roll_number }} | {{ b.student_email }}</small>
                </td>
                <td>
                  <span class="badge bg-dark me-1">{{ b.course_code }}</span>
                  <span>{{ b.examination_name }}</span>
                </td>
                <td>
                  <div>{{ b.slot_date }}</div>
                  <small class="text-muted">{{ b.start_time }} - {{ b.end_time }}</small>
                </td>
                <td>{{ b.examiner_name }}</td>
                <td>
                  <span
                    :class="[
                      'badge',
                      b.status === 'Completed' ? 'bg-success' : b.status === 'Booked' ? 'bg-primary' : 'bg-danger',
                    ]"
                  >
                    {{ b.status }}
                  </span>
                  <div v-if="b.rescheduled_by_admin" class="small text-warning fw-semibold mt-1">
                    Rescheduled
                  </div>
                </td>
                <td>
                  <div v-if="b.evaluation">
                    <strong>{{ b.evaluation.total_marks }} / {{ b.max_marks }}</strong>
                    <span class="badge bg-info text-dark ms-1">{{ b.evaluation.grade }}</span>
                  </div>
                  <span v-else class="text-muted small">Pending</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click="startBookingReschedule(b)">
                    Reschedule
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="tab === 'search'">
      <div class="card section-card p-4 mb-4">
        <h5 class="fw-bold mb-3">Search Records</h5>
        <div class="row g-2">
          <div class="col-md-7">
            <input
              type="text"
              class="form-control"
              v-model="searchQuery"
              @input="doSearch"
              placeholder="Search students, examiners, examinations, or bookings..."
            />
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="searchCategory" @change="doSearch">
              <option value="all">All</option>
              <option value="students">Students</option>
              <option value="examiners">Examiners</option>
              <option value="examinations">Examinations</option>
              <option value="bookings">Bookings</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary w-100" @click="doSearch">Search</button>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-md-6" v-if="searchCategory === 'all' || searchCategory === 'students'">
          <div class="card section-card p-3">
            <h6 class="fw-bold text-primary">Students ({{ (searchResults.students || []).length }})</h6>
            <ul class="list-group list-group-flush">
              <li v-for="s in searchResults.students" :key="s.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <strong>{{ s.name }}</strong> <span class="badge bg-secondary ms-1">{{ s.roll_number }}</span>
                  <div class="small text-muted">{{ s.email }} | {{ s.department }}</div>
                </div>
                <span class="badge bg-success">{{ s.status }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="col-md-6" v-if="searchCategory === 'all' || searchCategory === 'examiners'">
          <div class="card section-card p-3">
            <h6 class="fw-bold text-info">Examiners ({{ (searchResults.examiners || []).length }})</h6>
            <ul class="list-group list-group-flush">
              <li v-for="e in searchResults.examiners" :key="e.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <strong>{{ e.name }}</strong>
                  <div class="small text-muted">{{ e.email }} | {{ e.department }}</div>
                </div>
                <span class="badge bg-info text-dark">{{ e.designation }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="col-md-6" v-if="searchCategory === 'all' || searchCategory === 'examinations'">
          <div class="card section-card p-3">
            <h6 class="fw-bold text-success">Examinations ({{ (searchResults.examinations || []).length }})</h6>
            <ul class="list-group list-group-flush">
              <li v-for="ex in searchResults.examinations" :key="ex.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <span class="badge bg-dark me-1">{{ ex.course_code }}</span>
                  <strong>{{ ex.name }}</strong>
                  <div class="small text-muted">{{ ex.exam_type }} | Max Marks: {{ ex.max_marks }}</div>
                </div>
                <span class="badge bg-primary">{{ ex.status }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="col-md-6" v-if="searchCategory === 'all' || searchCategory === 'bookings'">
          <div class="card section-card p-3">
            <h6 class="fw-bold text-warning">Bookings ({{ (searchResults.bookings || []).length }})</h6>
            <ul class="list-group list-group-flush">
              <li v-for="b in searchResults.bookings" :key="b.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <strong>#{{ b.id }} {{ b.student_name }}</strong> → {{ b.examination_name }}
                  <div class="small text-muted">{{ b.slot_date }} ({{ b.start_time }}-{{ b.end_time }}) | {{ b.examiner_name }}</div>
                </div>
                <span class="badge bg-secondary">{{ b.status }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'jobs'" class="row g-4">
      <div class="col-lg-5">
        <div class="card section-card p-4 mb-4">
          <h5 class="fw-bold mb-3">Celery Background Jobs</h5>
          <div class="d-grid gap-3">
            <div class="p-3 border rounded-3 bg-light">
              <h6 class="fw-bold mb-1">Daily Examination Reminder</h6>
              <p class="small text-muted mb-2">
                Sends reminders to students with upcoming bookings via Google Chat, Email, and Notifications.
              </p>
              <button class="btn btn-primary btn-sm w-100" @click="runDailyReminder">
                Run Daily Reminder Job
              </button>
            </div>

            <div class="p-3 border rounded-3 bg-light">
              <h6 class="fw-bold mb-1">Monthly Examination Report</h6>
              <p class="small text-muted mb-2">
                Generates monthly examination summary in HTML and PDF formats for Admin.
              </p>
              <button class="btn btn-success btn-sm w-100" @click="runMonthlyReport">
                Generate Monthly Report
              </button>
            </div>
          </div>
        </div>

        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">Redis Cache Stats</h5>
          <ul class="list-group list-group-flush small">
            <li class="list-group-item d-flex justify-content-between">
              <span>Backend Mode:</span>
              <span class="badge bg-success">{{ dash.cache_info.mode || 'active' }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Active Keys:</span>
              <strong>{{ dash.cache_info.active_keys || 0 }}</strong>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Cache Hits:</span>
              <strong class="text-success">{{ dash.cache_info.hits || 0 }}</strong>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Cache Misses:</span>
              <strong class="text-secondary">{{ dash.cache_info.misses || 0 }}</strong>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Invalidations:</span>
              <strong class="text-warning">{{ dash.cache_info.invalidations || 0 }}</strong>
            </li>
          </ul>
        </div>
      </div>

      <div class="col-lg-7">
        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">Job Execution History</h5>
          <div class="table-responsive mb-3">
            <table class="table table-sm table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Job</th>
                  <th>Summary</th>
                  <th>Output</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in jobLogs" :key="log.id">
                  <td>
                    <span class="badge bg-primary">{{ log.job_name }}</span>
                    <div class="small text-muted">{{ (log.created_at || '').slice(0, 19).replace('T', ' ') }}</div>
                  </td>
                  <td class="small">{{ log.summary }}</td>
                  <td>
                    <div class="d-flex gap-1">
                      <button
                        v-if="log.has_html_preview"
                        class="btn btn-xs btn-outline-info btn-sm py-0"
                        @click="previewHtml = log.html_preview"
                      >
                        HTML
                      </button>
                      <a
                        v-if="log.artifact_path && log.job_name === 'monthly_report'"
                        :href="resolveUrl('/api/admin/reports/download/' + log.artifact_path)"
                        target="_blank"
                        class="btn btn-xs btn-outline-danger btn-sm py-0"
                      >
                        PDF
                      </a>
                      <a
                        v-if="log.artifact_path && log.job_name === 'csv_export'"
                        :href="resolveUrl('/api/student/exports/download/' + log.artifact_path)"
                        target="_blank"
                        class="btn btn-xs btn-outline-success btn-sm py-0"
                      >
                        CSV
                      </a>
                    </div>
                  </td>
                </tr>
                <tr v-if="jobLogs.length === 0">
                  <td colspan="3" class="text-center text-muted small py-3">
                    No jobs executed yet.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="previewHtml" class="border rounded p-3 bg-light">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <strong class="small text-primary">HTML Preview</strong>
              <button class="btn-close btn-sm" @click="previewHtml = ''"></button>
            </div>
            <div v-html="previewHtml" class="bg-white p-3 rounded border"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";
import EMP_API from "../services/api";

export default {
  name: "AdminPortal",
  emits: ["notify", "refresh-notifications"],
  data() {
    const today = new Date().toISOString().slice(0, 10);
    const nextWeek = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);
    return {
      tab: "dashboard",
      dash: { summary: {}, charts: {}, cache_info: {} },
      courses: [],
      exams: [],
      examiners: [],
      students: [],
      slots: [],
      bookings: [],
      jobLogs: [],
      previewHtml: "",

      editingCourse: null,
      courseForm: {
        code: "",
        name: "",
        department: "Computer Science & Engineering",
        credits: 4,
        semester: "Term 1 - 2026",
        status: "Active",
        description: "",
      },

      editingExam: null,
      examForm: {
        course_id: "",
        name: "",
        exam_type: "Viva",
        duration: 30,
        max_marks: 100,
        passing_marks: 40,
        slot_creation_start: today,
        slot_creation_end: nextWeek,
        slot_booking_start: today,
        slot_booking_end: nextWeek,
        status: "Slot Creation",
        slot_creation_open: true,
        slot_booking_open: false,
        instructions: "Join 5 minutes before the scheduled start time with valid ID.",
        examiner_ids: [],
      },

      activeRubricExam: null,
      rubrics: [],
      rubricForm: {
        criterion_name: "",
        max_marks: 25,
        weightage: 25,
        description: "",
      },

      editingExaminer: null,
      examinerForm: {
        name: "",
        email: "",
        username: "",
        password: "examiner123",
        contact_details: "",
        department: "Computer Science & Engineering",
        designation: "Assistant Professor",
        specialization: "",
        status: "Active",
        examination_ids: [],
      },

      slotToEdit: null,
      slotEditForm: {
        date: "",
        start_time: "",
        end_time: "",
        examiner_id: "",
        max_capacity: 1,
        venue: "",
        meeting_link: "",
        status: "Available",
        reason: "",
      },

      bookingToMove: null,
      bookingMoveForm: {
        new_slot_id: "",
        reason: "Rescheduled by Admin.",
      },

      searchQuery: "",
      searchCategory: "all",
      searchResults: {
        students: [],
        examiners: [],
        examinations: [],
        bookings: [],
      },
    };
  },
  mounted() {
    this.c1 = null;
    this.c2 = null;
    this.c3 = null;
    this.c4 = null;
    this.fetchAll();
  },
  beforeUnmount() {
    this.clearCharts();
  },
  methods: {
    resolveUrl(path) {
      return EMP_API.resolveUrl(path);
    },
    clearCharts() {
      if (this.c1) this.c1.destroy();
      if (this.c2) this.c2.destroy();
      if (this.c3) this.c3.destroy();
      if (this.c4) this.c4.destroy();
    },
    async fetchAll() {
      try {
        const [d, c, ex, exm, st, sl, bk, jl] = await Promise.all([
          EMP_API.get("/api/admin/dashboard"),
          EMP_API.get("/api/admin/courses"),
          EMP_API.get("/api/admin/examinations"),
          EMP_API.get("/api/admin/examiners"),
          EMP_API.get("/api/admin/students"),
          EMP_API.get("/api/admin/slots"),
          EMP_API.get("/api/admin/bookings"),
          EMP_API.get("/api/admin/jobs/logs"),
        ]);
        this.dash = d;
        this.courses = c.courses || [];
        this.exams = ex.examinations || [];
        this.examiners = exm.examiners || [];
        this.students = st.students || [];
        this.slots = sl.slots || [];
        this.bookings = bk.bookings || [];
        this.jobLogs = jl.logs || [];

        if (!this.examForm.course_id && this.courses.length > 0) {
          this.examForm.course_id = this.courses[0].id;
        }
        if (this.tab === "dashboard") {
          this.$nextTick(() => this.drawCharts());
        }
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    setTab(t) {
      this.tab = t;
      if (t === "dashboard") {
        this.$nextTick(() => this.drawCharts());
      } else if (t === "search") {
        this.doSearch();
      }
    },
    drawCharts() {
      const ch = this.dash.charts;
      if (!ch) return;
      this.clearCharts();

      const el1 = this.$refs.chartPopularExams;
      if (el1 && ch.popular_examinations) {
        this.c1 = new Chart(el1, {
          type: "bar",
          data: {
            labels: ch.popular_examinations.labels,
            datasets: [
              {
                label: "Bookings",
                data: ch.popular_examinations.bookings,
                backgroundColor: "rgba(13, 110, 253, 0.78)",
                borderRadius: 6,
              },
              {
                label: "Evaluations",
                data: ch.popular_examinations.evaluations,
                backgroundColor: "rgba(25, 135, 84, 0.78)",
                borderRadius: 6,
              },
            ],
          },
          options: { responsive: true, maintainAspectRatio: false },
        });
      }

      const el2 = this.$refs.chartExaminerWorkload;
      if (el2 && ch.examiner_workload) {
        this.c2 = new Chart(el2, {
          type: "bar",
          data: {
            labels: ch.examiner_workload.labels,
            datasets: [
              {
                label: "Slots",
                data: ch.examiner_workload.slots_created,
                backgroundColor: "rgba(102, 16, 242, 0.75)",
                borderRadius: 6,
              },
              {
                label: "Evaluated",
                data: ch.examiner_workload.evaluations_completed,
                backgroundColor: "rgba(253, 126, 20, 0.8)",
                borderRadius: 6,
              },
            ],
          },
          options: { responsive: true, maintainAspectRatio: false },
        });
      }

      const el3 = this.$refs.chartBookingTrends;
      if (el3 && ch.booking_trends) {
        this.c3 = new Chart(el3, {
          type: "doughnut",
          data: {
            labels: ch.booking_trends.labels,
            datasets: [
              {
                data: ch.booking_trends.data,
                backgroundColor: ["#0d6efd", "#198754", "#dc3545"],
              },
            ],
          },
          options: { responsive: true, maintainAspectRatio: false },
        });
      }

      const el4 = this.$refs.chartExamStatus;
      if (el4 && ch.exam_status_distribution) {
        this.c4 = new Chart(el4, {
          type: "pie",
          data: {
            labels: ch.exam_status_distribution.labels,
            datasets: [
              {
                data: ch.exam_status_distribution.data,
                backgroundColor: ["#6c757d", "#0dcaf0", "#0d6efd", "#ffc107", "#198754"],
              },
            ],
          },
          options: { responsive: true, maintainAspectRatio: false },
        });
      }
    },

    resetCourseForm() {
      this.editingCourse = null;
      this.courseForm = {
        code: "",
        name: "",
        department: "Computer Science & Engineering",
        credits: 4,
        semester: "Term 1 - 2026",
        status: "Active",
        description: "",
      };
    },
    editCourse(c) {
      this.editingCourse = c;
      this.courseForm = {
        code: c.code,
        name: c.name,
        department: c.department,
        credits: c.credits,
        semester: c.semester,
        status: c.status,
        description: c.description,
      };
    },
    async saveCourse() {
      try {
        if (this.editingCourse) {
          await EMP_API.put(`/api/admin/courses/${this.editingCourse.id}`, this.courseForm);
          this.$emit("notify", "Course updated.");
        } else {
          await EMP_API.post("/api/admin/courses", this.courseForm);
          this.$emit("notify", "Course created.");
        }
        this.resetCourseForm();
        await this.fetchAll();
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    async removeCourse(c) {
      if (!confirm(`Delete course '${c.code}'?`)) return;
      try {
        await EMP_API.delete(`/api/admin/courses/${c.id}`);
        this.$emit("notify", "Course deleted.");
        await this.fetchAll();
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },

    resetExamForm() {
      const today = new Date().toISOString().slice(0, 10);
      const nextWeek = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);
      this.editingExam = null;
      this.examForm = {
        course_id: this.courses.length ? this.courses[0].id : "",
        name: "",
        exam_type: "Viva",
        duration: 30,
        max_marks: 100,
        passing_marks: 40,
        slot_creation_start: today,
        slot_creation_end: nextWeek,
        slot_booking_start: today,
        slot_booking_end: nextWeek,
        status: "Slot Creation",
        slot_creation_open: true,
        slot_booking_open: false,
        instructions: "Join 5 minutes before the scheduled start time with valid ID.",
        examiner_ids: [],
      };
    },
    editExam(ex) {
      this.editingExam = ex;
      this.examForm = {
        course_id: ex.course_id,
        name: ex.name,
        exam_type: ex.exam_type,
        duration: ex.duration,
        max_marks: ex.max_marks,
        passing_marks: ex.passing_marks,
        slot_creation_start: ex.slot_creation_start,
        slot_creation_end: ex.slot_creation_end,
        slot_booking_start: ex.slot_booking_start,
        slot_booking_end: ex.slot_booking_end,
        status: ex.status,
        slot_creation_open: ex.slot_creation_open,
        slot_booking_open: ex.slot_booking_open,
        instructions: ex.instructions,
        examiner_ids: [...(ex.assigned_examiner_ids || [])],
      };
    },
    async saveExam() {
      try {
        if (this.editingExam) {
          await EMP_API.put(`/api/admin/examinations/${this.editingExam.id}`, this.examForm);
          this.$emit("notify", "Examination updated.");
        } else {
          await EMP_API.post("/api/admin/examinations", this.examForm);
          this.$emit("notify", "Examination created.");
        }
        this.resetExamForm();
        await this.fetchAll();
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    async removeExam(ex) {
      if (!confirm(`Delete examination '${ex.name}'?`)) return;
      try {
        await EMP_API.delete(`/api/admin/examinations/${ex.id}`);
        this.$emit("notify", "Examination deleted.");
        await this.fetchAll();
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    async flipSlotCreation(ex) {
      try {
        const res = await EMP_API.post(`/api/admin/examinations/${ex.id}/toggle-slot-creation`, {
          open: !ex.slot_creation_open,
        });
        this.$emit("notify", res.message);
        await this.fetchAll();
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    async flipSlotBooking(ex) {
      try {
        const res = await EMP_API.post(`/api/admin/examinations/${ex.id}/toggle-slot-booking`, {
          open: !ex.slot_booking_open,
        });
        this.$emit("notify", res.message);
        await this.fetchAll();
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    async flipResults(ex) {
      try {
        const res = await EMP_API.post(`/api/admin/examinations/${ex.id}/publish-results`, {
          publish: !ex.results_published,
        });
        this.$emit("notify", res.message);
        await this.fetchAll();
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },

    async openRubrics(ex) {
      this.activeRubricExam = ex;
      try {
        const res = await EMP_API.get(`/api/admin/examinations/${ex.id}/rubrics`);
        this.rubrics = res.rubrics || [];
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    async addRubric() {
      if (!this.activeRubricExam) return;
      try {
        await EMP_API.post(
          `/api/admin/examinations/${this.activeRubricExam.id}/rubrics`,
          this.rubricForm
        );
        this.rubricForm = { criterion_name: "", max_marks: 25, weightage: 25, description: "" };
        await this.openRubrics(this.activeRubricExam);
        await this.fetchAll();
        this.$emit("notify", "Rubric added.");
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    async removeRubric(r) {
      try {
        await EMP_API.delete(`/api/admin/rubrics/${r.id}`);
        await this.openRubrics(this.activeRubricExam);
        await this.fetchAll();
        this.$emit("notify", "Rubric deleted.");
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },

    resetExaminerForm() {
      this.editingExaminer = null;
