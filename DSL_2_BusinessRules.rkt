#lang racket

;; Domain-Specific Language (DSL) for Business Discount Rules
;; Tether AI Technologies - DSL Prototype 2
;; File: DSL_2_BusinessRules.rkt

;; Struct representing a business discount rule
(struct discount-rule (name condition action) #:transparent)

;; DSL Constructor: rule
;; Purpose: Creates a new business rule with a descriptive name, predicate condition, and action function.
(define (rule name condition action)
  (discount-rule name condition action))

;; DSL Interpreter/Engine: apply-rules
;; Purpose: Evaluates a list of discount rules against a total amount.
;; Returns the highest calculated discount amount among all qualifying rules.
(define (apply-rules total-amount rules)
  (displayln "==================================================")
  (displayln "   TETHER AI - BUSINESS DISCOUNT RULES ENGINE    ")
  (displayln "==================================================")
  (printf "Initial Total Amount: $~a~n" (~r total-amount #:precision '(= 2)))
  (displayln "Evaluating Rules...")
  (displayln "--------------------------------------------------")

  ;; Evaluate rules using foldl to find max discount
  (define best-discount
    (foldl (lambda (r max-discount)
             (define rule-name (discount-rule-name r))
             (define cond-fn (discount-rule-condition r))
             (define action-fn (discount-rule-action r))

             (if (cond-fn total-amount)
                 (let ([calculated-discount (action-fn total-amount)])
                   (printf "  [APPLIED] Rule '~a' -> Discount: $~a~n"
                           rule-name
                           (~r calculated-discount #:precision '(= 2)))
                   (max max-discount calculated-discount))
                 (begin
                   (printf "  [PASSED]  Rule '~a' -> Condition not met.~n" rule-name)
                   max-discount)))
           0
           rules))

  (define final-amount (- total-amount best-discount))
  (displayln "--------------------------------------------------")
  (printf "Best Discount Applied: $~a~n" (~r best-discount #:precision '(= 2)))
  (printf "Final Discounted Price: $~a~n" (~r final-amount #:precision '(= 2)))
  (displayln "==================================================")
  best-discount)

;; --- Sample Business Rules Setup & Demonstration ---

;; Rule 1: VIP Discount (15% off if total >= $100)
(define vip-rule
  (rule "VIP Discount"
        (lambda (t) (>= t 100))
        (lambda (t) (* t 0.15))))

;; Rule 2: Loyalty Perk ($10 off if total >= $50)
(define loyalty-rule
  (rule "Loyalty Perk"
        (lambda (t) (>= t 50))
        (lambda (t) 10.00)))

;; Rule 3: High Roller Special (20% off if total >= $200)
(define high-roller-rule
  (rule "High Roller Special"
        (lambda (t) (>= t 200))
        (lambda (t) (* t 0.20))))

;; Test execution with a $120 sale
(define discount-result
  (apply-rules 120 (list vip-rule loyalty-rule high-roller-rule)))
