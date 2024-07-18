#!/bin/zsh

cat > test.cpp << EOF
struct pthread_mutex_t;
struct pthread_mutexattr_t;
void pthread_mutex_init(pthread_mutex_t *mutex, const pthread_mutexattr_t *attr);
void f(pthread_mutex_t *mutex)
{
	pthread_mutex_init(mutex, 0); // no-warning
	pthread_mutex_init(mutex, 0); // expected-warning{{This lock has already been initialized}}
}
EOF

echo "Running Clang Static Analyzer..."

/home/gamesh411/clang-rwa/bin/clang \
  -cc1 \
  -internal-isystem /home/gamesh411/clang-rwa/lib/clang/19/include \
  -nostdsysteminc \
  -analyze \
  -analyzer-constraints=range \
  -setup-static-analyzer \
  -analyzer-checker=unix.MutexModeling \
  -std=c++11 \
  -analyzer-output text \
  -verify \
  test.cpp
