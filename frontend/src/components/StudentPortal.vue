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
            No published results yet.
          </div>
          <div v-for="r in dash.published_results" :key="r.id" class="border rounded-3 p-3 mb-2">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <span class="badge bg-dark me-1">{{ r.course_code }}</span>
                <strong>{{ r.examination_name }}</strong>
              </div>
              <span class="badge bg-success fs-6">
                {{ r.evaluation.total_marks }} / {{ r.max_marks }} ({{ r.evaluation.grade }})
              </span>
            </div>
            <p class="small text-muted mb-2 mt-1">
              <strong>Remarks:</strong> {{ r.evaluation.remarks }}
            </p>
            <button class="btn btn-sm btn-outline-primary" @click="getScorecard(r)">
              <i class="bi bi-file-earmark-pdf me-1"></i>Download Scorecard PDF
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'browse'">
      <div class="card section-card p-3 mb-4">
        <div class="row g-2 align-items-center">
          <div class="col-md-4">
            <input
              type="text"
              class="form-control"
              v-model="filter.q"
              @input="filterExams"
              placeholder="Search by examination name or course code..."
            />
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filter.course_id" @change="filterExams">
              <option value="">All Courses</option>
              <option v-for="c in dash.courses" :key="c.id" :value="c.id">{{ c.code }} - {{ c.name }}</option>
            </select>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filter.exam_type" @change="filterExams">
              <option value="">All Types</option>
              <option>Viva</option>
              <option>Practical</option>
              <option>Project Demo</option>
              <option>Assessment</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary w-100" @click="filterExams">
              Filter
            </button>
          </div>
        </div>
      </div>

      <div v-if="activeExam" class="card section-card p-4 mb-4 border-start border-4 border-primary">
        <div class="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h5 class="fw-bold mb-1 text-primary">
              Slots — {{ activeExam.name }} ({{ activeExam.course_code }})
            </h5>
            <div class="small text-muted">
              Instructions: {{ activeExam.instructions }}
            </div>
          </div>
          <button class="btn-close" @click="activeExam = null"></button>
        </div>

        <div v-if="activeExam.rubrics && activeExam.rubrics.length" class="mb-3">
          <strong class="small text-secondary d-block mb-1">Evaluation Criteria:</strong>
          <div class="d-flex flex-wrap gap-2">
            <span v-for="r in activeExam.rubrics" :key="r.id" class="badge bg-light text-dark border">
              {{ r.criterion_name }}: {{ r.max_marks }} marks ({{ r.weightage }}%)
            </span>
          </div>
        </div>

        <div class="table-responsive">
          <table class="table table-sm table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Date</th>
                <th>Time</th>
                <th>Examiner</th>
                <th>Venue</th>
                <th>Available Seats</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in examSlots" :key="s.id">
                <td>#{{ s.id }}</td>
                <td class="fw-semibold">{{ s.date }}</td>
                <td>{{ s.start_time }} - {{ s.end_time }}</td>
                <td>{{ s.examiner_name }}</td>
                <td class="small">{{ s.venue }}</td>
                <td><strong>{{ s.available_seats }}</strong> / {{ s.max_capacity }}</td>
                <td>
                  <span :class="['badge', s.status === 'Available' ? 'bg-success' : 'bg-warning text-dark']">
                    {{ s.status }}
                  </span>
                </td>
                <td>
                  <button
                    class="btn btn-sm btn-primary"
                    :disabled="s.status !== 'Available' || s.available_seats <= 0 || !activeExam.can_book_slots || isBooked(activeExam.id)"
                    @click="bookSlot(s)"
                  >
                    {{ isBooked(activeExam.id) ? 'Booked' : 'Book Slot' }}
                  </button>
                </td>
              </tr>
              <tr v-if="examSlots.length === 0">
                <td colspan="8" class="text-center text-muted py-3">No slots available yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="row g-3">
        <div v-for="ex in examList" :key="ex.id" class="col-md-6">
          <div class="card section-card p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <span class="badge bg-dark me-1">{{ ex.course_code }}</span>
                <span class="badge bg-info text-dark">{{ ex.exam_type }}</span>
              </div>
              <span :class="['badge', ex.can_book_slots ? 'bg-success' : 'bg-secondary']">
                {{ ex.can_book_slots ? 'Booking Open' : ex.status }}
              </span>
            </div>
            <h5 class="fw-bold mb-1">{{ ex.name }}</h5>
            <p class="small text-muted mb-2">{{ ex.course_name }} | Duration: {{ ex.duration }} mins | Max Marks: {{ ex.max_marks }}</p>
            <div class="small bg-light p-2 rounded mb-3">
              <div><strong>Booking Window:</strong> {{ ex.slot_booking_start }} to {{ ex.slot_booking_end }}</div>
              <div><strong>Available Slots:</strong> {{ ex.available_slots_count }} open (Total: {{ ex.slots_count }})</div>
            </div>
            <div class="d-flex justify-content-between align-items-center mt-auto">
              <span v-if="isBooked(ex.id)" class="badge bg-primary">
                Booked
              </span>
              <span v-else class="small text-muted">1 slot per exam</span>
              <button class="btn btn-sm btn-outline-primary fw-semibold" @click="loadExamSlots(ex)">
                View Slots
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'bookings'" class="card section-card p-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="fw-bold mb-0">My Examination Bookings</h5>
        <button class="btn btn-sm btn-success" @click="exportCsv">
          Export CSV
        </button>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Examination</th>
              <th>Date &amp; Time</th>
              <th>Examiner</th>
              <th>Venue</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in dash.bookings" :key="b.id">
              <td>#{{ b.id }}</td>
              <td>
                <span class="badge bg-dark me-1">{{ b.course_code }}</span>
                <strong>{{ b.examination_name }}</strong>
                <div class="small text-muted">{{ b.exam_type }}</div>
              </td>
              <td>
                <div>{{ b.slot_date }}</div>
                <small class="text-muted">{{ b.start_time }} - {{ b.end_time }}</small>
              </td>
              <td>{{ b.examiner_name }}</td>
              <td class="small">
                <div>{{ b.venue }}</div>
                <a v-if="b.meeting_link && b.status === 'Booked'" :href="b.meeting_link" target="_blank">Meeting Link</a>
              </td>
              <td>
                <span
                  :class="[
                    'badge',
                    b.status === 'Completed' ? 'bg-success' : b.status === 'Booked' ? 'bg-primary' : 'bg-danger',
                  ]"
                >
                  {{ b.status }}
                </span>
                <div v-if="b.rescheduled_by_admin" class="small text-warning mt-1">
                  {{ b.admin_notes }}
                </div>
              </td>
              <td>
                <button
                  v-if="b.status === 'Booked'"
                  class="btn btn-sm btn-outline-danger"
                  @click="cancelBooking(b)"
                >
                  Cancel
                </button>
                <button
                  v-else-if="b.evaluation && b.results_published"
                  class="btn btn-sm btn-outline-success"
                  @click="tab = 'results'"
                >
                  Result ({{ b.evaluation.total_marks }}/{{ b.max_marks }})
                </button>
                <span v-else class="small text-muted">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="tab === 'results'">
      <div v-if="(dash.published_results || []).length === 0" class="card section-card p-5 text-center text-muted">
        <h5>No Published Results Yet</h5>
        <p class="small mb-0">Results will appear here once published by the Admin.</p>
      </div>

      <div v-for="b in dash.published_results" :key="b.id" class="card section-card p-4 mb-4">
        <div class="d-flex flex-wrap justify-content-between align-items-center border-bottom pb-3 mb-3">
          <div>
            <span class="badge bg-dark me-2">{{ b.course_code }} - {{ b.course_name }}</span>
            <span class="badge bg-info text-dark">{{ b.exam_type }}</span>
            <h4 class="fw-bold mt-2 mb-0">{{ b.examination_name }}</h4>
            <small class="text-muted">
              Examiner: <strong>{{ b.examiner_name }}</strong> | Date: {{ b.slot_date }}
            </small>
          </div>
          <div class="text-end">
            <div class="display-6 fw-bold text-primary">
              {{ b.evaluation.total_marks }} <span class="fs-5 text-muted">/ {{ b.max_marks }}</span>
            </div>
            <span class="badge bg-success me-1">Grade {{ b.evaluation.grade }} ({{ b.evaluation.percentage }}%)</span>
            <span :class="['badge', b.evaluation.passed ? 'bg-success' : 'bg-danger']">
              {{ b.evaluation.passed ? 'PASS' : 'FAIL' }}
            </span>
          </div>
        </div>

        <div class="alert alert-light border mb-3">
          <strong>Remarks:</strong>
          {{ b.evaluation.remarks || 'Good.' }}
        </div>

        <div v-if="b.evaluation.rubric_breakdown && b.evaluation.rubric_breakdown.length" class="table-responsive mb-3">
          <table class="table table-sm table-bordered">
            <thead class="table-light">
              <tr>
                <th>Criterion</th>
                <th>Weightage</th>
                <th>Marks</th>
                <th>Comment</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rb in b.evaluation.rubric_breakdown" :key="rb.rubric_id">
                <td class="fw-semibold">{{ rb.criterion_name }}</td>
                <td>{{ rb.weightage }}%</td>
                <td><strong>{{ rb.marks_awarded }}</strong> / {{ rb.max_marks }}</td>
                <td class="small text-muted">{{ rb.comment }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="text-end">
          <button class="btn btn-primary btn-sm" @click="getScorecard(b)">
            <i class="bi bi-file-earmark-pdf-fill me-1"></i>Download Scorecard PDF
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EMP_API from "../services/api";

export default {
  name: "StudentPortal",
  emits: ["notify", "refresh-notifications"],
  data() {
    return {
      tab: "dashboard",
      dash: {
        summary: {},
        courses: [],
        available_examinations: [],
        available_slots: [],
        upcoming_examinations: [],
        bookings: [],
        active_booked_exam_ids: [],
        published_results: [],
      },
      filter: {
        q: "",
        course_id: "",
        exam_type: "",
        status: "",
      },
      examList: [],
      activeExam: null,
      examSlots: [],
    };
  },
  mounted() {
    this.fetchDash();
  },
  methods: {
    async fetchDash() {
      try {
        const res = await EMP_API.get("/api/student/dashboard");
        this.dash = res;
        this.examList = res.available_examinations || [];
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    async filterExams() {
