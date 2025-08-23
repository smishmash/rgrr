(ns rgrr.server
  (:require [clojure.string :as s]))

(defn proxy?
  [req context]
  (s/starts-with? (.getRequestURI req) "/simulations/"))
