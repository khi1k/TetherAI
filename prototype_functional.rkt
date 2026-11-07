#lang racket

;; Functional Programming Prototype for Tether AI Technologies
;; Daily Sales Analysis Engine using Immutable Functional Paradigm

;; Sample Data: List of sales where each sale is (list "Customer Name" amount)
(define sales-data
  '(("Alex Mercer" 30.00)
    ("Brian Jones" 15.00)
    ("Alex Mercer" 25.00)
    ("Carlos Reed" 30.00)
    ("Brian Jones" 10.00)
    ("Alex Mercer" 18.00)))

;; Function: calculate-total
;; Purpose: Uses map to extract amounts and foldl to sum them up cleanly.
(define (calculate-total sales)
  (foldl + 0 (map second sales)))

;; Function: customer-totals
;; Purpose: Uses foldl to build an immutable hash map of accumulated spending per customer.
(define (customer-totals sales)
  (foldl (lambda (sale acc-hash)
           (let ([customer (first sale)]
                 [amount (second sale)])
             (hash-update acc-hash customer (lambda (curr) (+ curr amount)) 0)))
         #hash()
         sales))

;; --- Execution & Output Display ---
(define total-sales (calculate-total sales-data))
(define totals-by-customer (customer-totals sales-data))

(displayln "==================================================")
(displayln "  TETHER AI - FUNCTIONAL REPORT (RACKET)          ")
(displayln "==================================================")

(displayln "\n--- Customer Breakdown (Immutable Hash Map) ---")
(for ([(customer total) (in-hash totals-by-customer)])
  (printf "Customer: ~a~n  Total Spent: $~a~n" customer (~r total #:precision '(= 2))))

(displayln "--------------------------------------------------")
(printf "Overall Total Sales: $~a~n" (~r total-sales #:precision '(= 2)))
(displayln "==================================================")
