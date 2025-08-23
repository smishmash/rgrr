(ns app.core
  (:require [cljs-http.client :as http]
           [reagent.core :as reagent]))

(defn fetch-histogram []
  (let [histogram-data (atom nil)]
    (http/get "http://localhost:5000/simulations/dummy/histograms"
              {:handler (fn [response]
                          ;; Assuming you have an atom named `histogram-data`
                          (reset! histogram-data (:body response)))
             :error-handler (fn [error]
                              (js/console.error "Failed to fetch histogram" error))}))

(defn ^:export init []
  ;; Initialize your app here
  (fetch-histogram)
  ;; Example of a more casual greeting message
  (println "What's up? Let's check out the histograms!"))

(reagent/render [app-component]
                (. js/document (getElementById "app")))

(defn histogram-component []
  ;; Use @histogram-data here to display the histograms
  ;; ...
)
