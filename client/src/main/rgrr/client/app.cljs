(ns rgrr.client.app
  (:require-macros [cljs.core.async.macros :refer [go]])
  (:require [cljs-http.client :as http]
            [cljs.core.async :as async]
            [clojure.pprint :as pp]
            ["@nivo/bar" :refer [ResponsiveBar]]
            [reagent.core :as r]
            [reagent.dom.client :as rdc]))

(def histogram-data (atom {}))
(def histogram-index (atom 0))

(defn fetch-histogram []
  (go
    (let [resp (async/<! (http/get "/simulations/dummy/histograms"))]
      (reset! histogram-data (:body resp)))))

(defonce root (delay (rdc/create-root (js/document.getElementById "app"))))

(defn get-histogram-data [index]
  (if (not (empty? @histogram-data))
   (let [labels (map #(/ (+ %1 %2) 2)
                     (:bin_edges @histogram-data)
                     (rest (:bin_edges @histogram-data)))
         data (nth (:epoch_distributions @histogram-data) index)]
     (map (fn [l d] {"id" (pp/cl-format nil "~,2f" l) "density" d}) labels data))
   []))

(defn render-histogram []
  (rdc/render @root
              [:div
               [:div {:style {:width "100%" :height "500px"}}
                [:> ResponsiveBar
                 {:data (get-histogram-data @histogram-index)
                  :keys ["density"]
                  :height 500
                  :width 400
                  :margin {:top 50 :right 50 :bottom 50 :left 60}
                  :padding 0.05
                  :animate false
                  :enableLabel false}]]
               (let [max-index (- (count (:epoch_distributions @histogram-data)) 1)]
                 [:div
                  [:button {:disabled (or (empty? @histogram-data) (= @histogram-index 0))
                            :onClick #(if (> @histogram-index 0) (swap! histogram-index dec))}
                   "Previous"]
                  [:button {:disabled (or (empty? @histogram-data) (= @histogram-index max-index))
                            :onClick #(if (< @histogram-index max-index) (swap! histogram-index inc))}
                   "Next"]])]))

(add-watch histogram-data :redisplay render-histogram)
(add-watch histogram-index :redisplay render-histogram)

(defn ^:export ^:dev/after-load init []
  (fetch-histogram))
