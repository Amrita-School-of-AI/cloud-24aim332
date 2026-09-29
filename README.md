# 24AIM332 · Introduction to Cloud Computing

**Dr. Abhijith Anandakrishnan**, Assistant Professor
Amrita School of AI, Amrita Vishwa Vidyapeetham, Coimbatore

L-T-P-C 3-0-2-4 · Semester 5 · B.Tech Artificial Intelligence and Data Science (minor in Medical Engineering)

---

All course material lives here. Everything is a PDF built from source, so it is
the same on every machine and works offline.

## New here? Start with the Getting Started guide

**[handbook/student-guide.pdf](handbook/student-guide.pdf)** takes you from a laptop with nothing installed to a working setup: a GitHub SSH key, your own fork, a cloud account with a spending alert already set, and Docker, kubectl and a local Kubernetes cluster. About forty minutes, once.

Then read **[handbook/course-handbook.pdf](handbook/course-handbook.pdf)** for the
week-by-week plan, the marks breakdown and the policies.


### Handbook

| Document | Size |
|---|---|
| [course handbook](handbook/course-handbook.pdf) | 585 KB |
| [student guide](handbook/student-guide.pdf) | 768 KB |

### Slide decks

| Document | Size |
|---|---|
| [i01 cloud fundamentals](slides/i01-cloud-fundamentals.pdf) | 231 KB |
| [i02 virtualization and containers](slides/i02-virtualization-and-containers.pdf) | 243 KB |
| [i03 kubernetes](slides/i03-kubernetes.pdf) | 254 KB |
| [i04 iac and cicd](slides/i04-iac-and-cicd.pdf) | 229 KB |
| [i05 case study echno](slides/i05-case-study-echno.pdf) | 192 KB |
| [i06 case study digital twin](slides/i06-case-study-digital-twin.pdf) | 205 KB |

### Assignments

| Document | Size |
|---|---|
| [class assignment](assignments/class-assignment.pdf) | 515 KB |

### Lab sheets

| Document | Size |
|---|---|
| [icclab1 first instance and teardown](labs/icclab1-first-instance-and-teardown.pdf) | 350 KB |
| [icclab3 containerise an application](labs/icclab3-containerise-an-application.pdf) | 387 KB |
| [icclab5 kubernetes deployment](labs/icclab5-kubernetes-deployment.pdf) | 447 KB |
| [icclab7 infrastructure as code](labs/icclab7-infrastructure-as-code.pdf) | 397 KB |
| [icclab8 pipeline from commit to running](labs/icclab8-pipeline-from-commit-to-running.pdf) | 357 KB |

### Coding exercises

| Exercise | Folder |
|---|---|
| [icc-ex02-kubernetes-manifest](exercises/icc-ex02-kubernetes-manifest/icc-ex02-kubernetes-manifest.pdf) | `icc-ex02-kubernetes-manifest` |

---

## Working the coding exercises

Each exercise folder contains a problem statement PDF, a `starter/` file to
edit, the checker in `tests/`, and `selfcheck.sh`. Work in your own fork:

```bash
cd exercises/icc-ex02-kubernetes-manifest
cp starter/manifest.yaml ../../submissions/icc-ex02-kubernetes-manifest/AIE23001.yaml
# edit it, then:
./selfcheck.sh ../../submissions/icc-ex02-kubernetes-manifest/AIE23001.yaml
```

Submit one file, named for your roll number. The class assignment is a
repository plus a report; the course handbook gives the stages, marks and
deadline.

## Licence and reuse

Teaching material for Amrita School of AI. You are welcome to read, learn from and adapt
it with attribution. Please do not redistribute it as your own course.

*Odd Semester 2026-27*
