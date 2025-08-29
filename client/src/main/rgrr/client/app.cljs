(ns rgrr.client.app
  (:require-macros [cljs.core.async.macros :refer [go]])
  (:require [cljs-http.client :as http]
            [cljs.core.async :as async]
            [clojure.pprint :as pp]
            ["@nivo/bar" :refer [ResponsiveBar]]
            [reagent.core :as r]
            [reagent.dom.client :as rdc]))

(def histogram-data (atom {}))
(def histogram-index (r/atom 0))
(def histogram-current (r/atom ()))

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
  (let [data (get-histogram-data @histogram-index)
        epoch-max (- (count (:epoch_distributions @histogram-data)) 1)]
    (rdc/render @root
                [(fn []
                   [:div
                    [:div {:style {:width "100%" :height "500px"}}
                     [:> ResponsiveBar
                      {:data @histogram-current
                       :keys ["density"]
                       :height 500
                       :width 400
                       :margin {:top 50 :right 50 :bottom 50 :left 60}
                       :padding 0.05
                       :enableLabel false}]]
                    [:div
                     [:button {:disabled (or (empty? @histogram-data) (= @histogram-index 0))
                               :onClick #(if (> @histogram-index 0) (swap! histogram-index dec))}
                      "Previous"]
                     [:button {:disabled (or (empty? @histogram-data) (= @histogram-index epoch-max))
                               :onClick #(if (< @histogram-index epoch-max) (swap! histogram-index inc))}
                      "Next"]]])])))

(defn update-current []
  (reset! histogram-current (get-histogram-data @histogram-index)))

(add-watch histogram-data :redisplay render-histogram)
(add-watch histogram-data :set-epoch update-current)
(add-watch histogram-index :set-epoch update-current)

(defn ^:export ^:dev/after-load init []
  (fetch-histogram))
