(ns rgrr.client.app
  (:require-macros [cljs.core.async.macros :refer [go]])
  (:require [cljs-http.client :as http]
            [cljs.core.async :as async]
            [clojure.pprint :as pp]
            ["@nivo/bar" :refer [ResponsiveBar]]
            [reagent.core :as r]
            [reagent.dom.client :as rdc]
            [shadow.css :refer (css)]))

(def simulation-config
  {:nodes 100
   :epochs 10
   :resources_per_node 1
   :operations [{:type "preferential" :resources_added 10}]})

(defonce current-view (r/atom :list)) ; :list or :details
(defonce simulation-id (r/atom nil)) ; To store the ID of the created simulation
(defonce simulation-details (r/atom nil)) ; To store details of the selected simulation

(defonce simulation-list (r/atom []))

(def histogram-data (atom {}))
(def histogram-index (r/atom 0))
(def histogram-current (r/atom ())) 

(defn fetch-simulation-list []
  (go
    (let [resp (async/<! (http/get "/simulations"))]
      (reset! simulation-list (:body resp)))))

(defn load-simulation-histogram []
  (go
    (let [id @simulation-id
          resp (async/<! (http/get (str "/simulations/" id "/histograms")))]
      (reset! histogram-data (:body resp))
      (reset! histogram-index 0)))) ; Reset index to 0 when loading a new simulation

(defn create-and-fetch-simulation []
  (go
    (let [resp (async/<! (http/post "/simulations" {:json-params simulation-config}))
          id (:id (:body resp))]
      (js/console.log (str "Created simulation with ID: " id))
      (async/<! (http/post (str "/simulations/" id "/run")))
      (reset! simulation-id id)
      (async/<! (fetch-simulation-list)))))

(defonce histogram-root (delay (rdc/create-root (js/document.getElementById "app"))))
(defonce simulations-root (delay (rdc/create-root (js/document.getElementById "app-simulations"))))

(defn get-histogram-data [index]
  (if (not (empty? @histogram-data))
   (let [labels (map #(/ (+ %1 %2) 2)
                     (:bin_edges @histogram-data)
                     (rest (:bin_edges @histogram-data)))
         data (nth (:epoch_distributions @histogram-data) index)]
     (map (fn [l d] {"id" (pp/cl-format nil "~,2f" l) "density" d}) labels data))
   []))

(defn fetch-simulation-details [id]
  (go
    (let [resp (async/<! (http/get (str "/simulations/" id)))]
      (reset! simulation-details (:body resp)))))

(defn render-simulation-list-panel []
  [:div {:style {:border-bottom "1px solid #ccc" :padding "10px" :margin-bottom "10px"}}
   [:h3 "Simulations"]
   [:ul
    (for [id @simulation-list]
      [:li {:key id
            :on-click #(do (reset! simulation-id id) (fetch-simulation-details id) (reset! current-view :details))
            :style {:cursor "pointer" :text-decoration (if (= id @simulation-id) "underline" "none")}} 
       id])]])

(defn render-header []
  [:div
   {:class (css :shadow {:color "red"})}
   ;; {:style {:width "100%" :text-align "center" :color "red"}}
   [:h2 "Epoch " @histogram-index]])

(defn render-chart []
  [:div {:style {:width "100%" :height "500px" :border "1px solid black"}}
   [:> ResponsiveBar
    {:data @histogram-current
     :keys ["density"]
     :height 500
     :width 400
     :defaultHeight 500
     :defaultWidth 400
     :margin {:top 50 :right 50 :bottom 50 :left 60}
     :padding 0.05
     :enableLabel false}]])

(defn render-controls []
  (let [epoch-max (- (count (:epoch_distributions @histogram-data)) 1)]
    [:div
     [:button {:disabled (or (empty? @histogram-data) (= @histogram-index 0))
               :onClick #(if (> @histogram-index 0) (swap! histogram-index dec))}
      "Previous"]
     [:input {:type "text"
              :value @histogram-index
              :onChange (fn [e]
                          (let [new-epoch-str (-> e .-target .-value)
                                new-epoch (when (and new-epoch-str (re-matches #"\d+" new-epoch-str))
                                            (js/parseInt new-epoch-str 10))]
                            ;; Ensure the input is a valid integer and in range before updating the state
                            (when (and new-epoch (<= 0 new-epoch epoch-max))
                              (reset! histogram-index new-epoch))))}]
     [:button {:disabled (or (empty? @histogram-data) (= @histogram-index epoch-max))
               :onClick #(if (< @histogram-index epoch-max) (swap! histogram-index inc))}
      "Next"]]))

(defn render-histogram []
  (rdc/render @histogram-root
              [(fn []
                 [:div
                  [render-header]
                  [render-chart]
                  [render-controls]])]))

(defn render-simulation-detail-panel []
  [:div
   [:button {:on-click #(reset! current-view :list)} "Back to List"]
   (when @simulation-details
     [:div
      [:h3 (str "Simulation Details: " (:id @simulation-details))]
      [:p (str "Nodes: " (:nodes @simulation-details))]
      [:p (str "Epochs: " (:epochs @simulation-details))]
      [:p (str "Resources per Node: " (:resources_per_node @simulation-details))]
      [:p (str "Seed: " (:seed @simulation-details))]
      [:h4 "Operations:"]
      [:ul
       (for [op (:operations @simulation-details)]
         [:li {:key (random-uuid)}
          [:p (str "Type: " (:type op))]
          (when (:resources_added op)
            [:p (str "Resources Added: " (:resources_added op))])
          (when (:tax_rate op)
            [:p (str "Tax Rate: " (:tax_rate op))])
          (when (:expenditure op)
            [:p (str "Expenditure: " (:expenditure op))])])]])])

(defn render-simulations-panel []
  (rdc/render @simulations-root
              [(fn []
                 (if (= @current-view :list)
                   [render-simulation-list-panel]
                   [render-simulation-detail-panel]))]))

(defn update-current []
  (reset! histogram-current (get-histogram-data @histogram-index)))

(add-watch histogram-data :redisplay render-histogram)
(add-watch histogram-data :set-epoch update-current)
(add-watch histogram-index :set-epoch update-current)
(add-watch simulation-list :redisplay render-simulations-panel)
; (add-watch simulation-id :redisplay load-simulation-histogram) ; Removed, as details view will handle loading

(defn ^:export ^:dev/after-load init []
  (go
    (async/<! (fetch-simulation-list))
    (when (empty? @simulation-list)
      (async/<! (create-and-fetch-simulation)))
    (render-histogram)
    (render-simulations-panel)))
