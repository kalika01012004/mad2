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
