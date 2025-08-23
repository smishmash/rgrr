(ns my-component.core (:require [reagent.core :as reagent :refer [atom]]))

(defn fetch-histogram! [url]
  (let [histogram-data (atom nil)]
    (js/console.log "Fetching histogram...")
    (.fetch js/window
            #js {:method "GET"
                 :url url
                 :headers #js {"Content-Type" "application/json"}
                 :onLoad #(reset! histogram-data (js->clj (.jsonParse %)))
                 :onError #(js/console.error "Error fetching histogram data")})
    histogram-data))

(defn render-histogram [histogram-data]
  [:div
   [:h1 "Histogram"]
   [:svg {:width 600 :height 400}
    ;; Assuming the histogram data is in a format that can be directly used to create SVG elements
    ;; This is a placeholder for the actual SVG rendering logic
    ]])

(defn my-component []
  (let [histogram-data (fetch-histogram! "/simulations/dummy/histograms")]
    [:div
     [:button {:on-click #(reset! histogram-data (fetch-histogram! "/simulations/dummy/histograms"))}
      "Refresh Histogram"]
     [:div (render-histogram @histogram-data)]]))

(reagent/render [my-component] (.getElementById js/document "app"))
